app.factory('ApiService', function($http) {
    var apiBaseUrl = 'http://localhost:5000'; // Adjust the port if necessary

    return {
        createUser: function(user) {
            console.log("ApiService: Creating user", user);
            return $http.post(apiBaseUrl + '/create_user', user);
        },
        authenticateUser: function(user) {
            console.log("ApiService: Authenticating user", user);
            return $http.post(apiBaseUrl + '/authenticate_user', user);
        },
        updateUserEmail: function(key, email) {
            console.log("ApiService: Updating email", email);
            return $http.put(apiBaseUrl + '/update_user_email', { email: email }, {
                headers: { 'Authorization': key }
            });
        },
        updateUserPassword: function(key, password) {
            console.log("ApiService: Updating password");
            return $http.put(apiBaseUrl + '/update_user_password', { password: password }, {
                headers: { 'Authorization': key }
            });
        },
        createOrder: function(key, order) {
            console.log("ApiService: Creating order", order);
            return $http.post(apiBaseUrl + '/create_order', order, {
                headers: { 'Authorization': key }
            });
        },
        listOrders: function(key) {
            console.log("ApiService: Listing orders");
            return $http.get(apiBaseUrl + '/list_orders', {
                headers: { 'Authorization': key }
            });
        }
    };
});
