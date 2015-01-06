'use strict';

/**
 * @ngdoc overview
 * @name webClientApp
 * @description
 * # webClientApp
 *
 * Main module of the application.
 */
angular.module('webClientApp', [
    'config',
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngSanitize',
    'ngTouch',
    'ui.router'
]).config(function ($stateProvider, $urlRouterProvider) {
  $urlRouterProvider.otherwise("/");

  $stateProvider.state('index', {
      url: "/",
      views: {
        "nav": { templateUrl: "views/nav.html" },
        "main": {
          templateUrl: "views/main.html",
          controller: "MainCtrl",
          resolve: {
            articles: function (parcClient) {
              return parcClient.getArticles();
            }
          }
        }
      }

  });

  $stateProvider.state('article', {
      url: "/article/:articleId",
      views: {
        "nav": { templateUrl: "views/nav.html" },
        "main": {
          templateUrl: "views/article.html",
          controller: "ArticleCtrl",
          resolve: {
            article: function (parcClient, $stateParams) {
              return parcClient.getArticle($stateParams.articleId);
            }
          }
        }
      }

  });
});
