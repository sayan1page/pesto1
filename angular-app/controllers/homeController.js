app.controller('HomeController', function($scope, $location, ApiService) {
    var authKey = sessionStorage.getItem('authKey');
    console.log("HomeController: Loaded with authKey", authKey);

    if (!authKey) {
        console.warn("HomeController: No authKey found, redirecting to login");
        $location.path('/login');
    }

    $scope.updateEmail = function() {
        console.log("HomeController: Updating email to", $scope.newEmail);
        ApiService.updateUserEmail(authKey, $scope.newEmail)
            .then(function(response) {
                alert("Email updated successfully!");
                console.log("HomeController: Email updated", response);
            })
            .catch(function(error) {
                alert("Error updating email!");
                console.error("HomeController: Error updating email", error);
            });
    };

    $scope.updatePassword = function() {
        console.log("HomeController: Updating password");
        ApiService.updateUserPassword(authKey, $scope.newPassword)
            .then(function(response) {
                alert("Password updated successfully!");
                console.log("HomeController: Password updated", response);
            })
            .catch(function(error) {
                alert("Error updating password!");
                console.error("HomeController: Error updating password", error);
            });
    };

    $scope.createOrder = function() {
        console.log("HomeController: Creating order", $scope.order);
        ApiService.createOrder(authKey, $scope.order)
            .then(function(response) {
                alert("Order created successfully!");
                console.log("HomeController: Order created", response);
            })
            .catch(function(error) {
                alert("Error creating order!");
                console.error("HomeController: Error creating order", error);
            });
    };

    $scope.listOrders = function() {
        console.log("HomeController: Listing orders");
        ApiService.listOrders(authKey)
            .then(function(response) {
                $scope.orders = response.data.orders;
                console.log("HomeController: Orders listed", $scope.orders);
            })
            .catch(function(error) {
                alert("Error fetching orders!");
                console.error("HomeController: Error fetching orders", error);
            });
    };
});
