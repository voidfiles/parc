'use strict';


angular.module('webClientApp').factory('parcClient', function ($http, $q, appConfig) {
    var articles = [];
    var articlesById = {};
    var loadedArticles = false;
    var loadingArticles = false;

    var loadArticles = function (before_id) {
      loadingArticles = true;

      var params = {
        count: 20
      };

      if (before_id) {
        params.before_id = before_id;
      }

      var req = {
        method: 'GET',
        url: appConfig.api + '/articles',
        params: params,
      }
      console.log('making request', req);
      $http(req).success(function (data) {
        articles.push.apply(articles, data.data);
        angular.forEach(data.data, function (newArticle) {
          var oldArticle = articlesById[newArticle.id];
          if (oldArticle) {
            angular.extend(articlesById[newArticle.id], newArticle);
          } else {
            articlesById[newArticle.id] = newArticle;
          }
        });
        if (data.meta.has_more) {
          loadArticles(data.meta.min_id);
        } else {
          loadingArticles = false;
          loadedArticles = true;
        }
      }).error(function () {
        loadingArticles = false;
      });
    };

    var _getArticle = function (articleId) {
      return $q(function (resolve, reject) {
        var req = {
          method: 'GET',
          url: appConfig.api + '/articles/' + articleId,
        };
        $http(req).success(function (data) {
          resolve(data.data);
        }).error(function () {
          reject();
        });
      });
    };

    return {
      getArticles: function () {
        if (!loadedArticles && !loadingArticles) {
          loadArticles();
        }

        return articles;
      },
      getArticle: function (articleId) {
        var currentArticle = articlesById[articleId];
        if (currentArticle) {
          return currentArticle;
        }
        console.log('yo');
        return _getArticle(articleId);
      }
    }
});
