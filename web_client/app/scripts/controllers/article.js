'use strict';

/**
 * @ngdoc function
 * @name webClientApp.controller:AboutCtrl
 * @description
 * # AboutCtrl
 * Controller of the webClientApp
 */
angular.module('webClientApp')
  .controller('ArticleCtrl', function ($scope, article) {
    $scope.article = article;
  });
