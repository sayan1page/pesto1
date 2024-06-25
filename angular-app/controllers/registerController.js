app.controller('RegisterController', function($scope, $location, ApiService) {
    $scope.register = function() {
        console.log("RegisterController: Registering user", $scope.user);
        ApiService.createUser($scope.user)
            .then(function(response) {
                alert("User registered successfully!");
                console.log("RegisterController: User registered", response);
                $location.path('/login');
            })
            .catch(function(error) {
                alert("Error registering user!");
                console.error("RegisterController: Error registering user", error);
            });
    };
});
