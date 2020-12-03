$(document).ready(function () {
    var tour = new Tour({
        steps: [
            {
                element: "#data-loading-div",
                title: "#1 Load your data",
                content: "Content of my step"
            }]
    });

    // Initialize the tour
    tour.init();



    $("#button-start").on('click',function(){
        // Start the tour
        tour.start();
    });
});