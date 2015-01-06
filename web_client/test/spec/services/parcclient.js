'use strict';

describe('Service: parcClient', function () {

  // load the service's module
  beforeEach(module('webClientApp'));

  // instantiate service
  var parcClient;
  beforeEach(inject(function (_parcClient_) {
    parcClient = _parcClient_;
  }));

  it('should do something', function () {
    expect(!!parcClient).toBe(true);
  });

});
