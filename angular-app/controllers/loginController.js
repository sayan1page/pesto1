app.controller('LoginController', function($scope, $location, ApiService) {
    $scope.login = function() {
        console.log("LoginController: Logging in user", $scope.user);
        ApiService.authenticateUser($scope.user)
            .then(function(response) {
                sessionStorage.setItem('authKey', response.data.key);
                console.log("LoginController: User authenticated, key stored", response.data.key);
                $location.path('/home');
            })
            .catch(function(error) {
                alert("Invalid credentials!");
                console.error("LoginController: Error authenticating user", error);
            });
    };
});
