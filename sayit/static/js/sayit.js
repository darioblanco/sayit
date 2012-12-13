$(document).ready(function() {
    $('#editTask').live('click', function (){
        timestamp = $(this)[0].attributes.value.value;
        old_title = $('#' + timestamp + '_title')[0].textContent

        // Edit task dialog
        $('#editTaskDialog').modal()
        $('#new-task-text').attr("placeholder", old_title);
        $('#task-timestamp').attr("value", timestamp);
    });

    $('#deleteTask').live('click', function (){
        timestamp = $(this)[0].attributes.value.value;
        $.post("/task/delete", {task_id: timestamp},
            function() {
                $(".alert").alert("Task deleted successfully");
                location.reload();
        })
        .error(function() { $(".alert").alert("Unable to delete the task");})
    });

    // Pick all the task breadcrumbs and set the completed with line-through
    $('ul').filter(function() {
        return this.id.match('_title');
    }).each(function(){
        completed = $(this).attr("value");
        if (completed == "True"){
            $(this).css("text-decoration","line-through");
        }
    })

    // Change task status
    $('#task-row').live('click', function (){
        console.log("status");
        timestamp = $(this).children().attr("id").replace('_title', '');
        status = $(this).children().attr("value");
        console.log(status);
        if (status == "False"){
            status = "True";
        } else {
            status = "False";
        }
        console.log(status);
        $.post("/task/status", {task_id: timestamp, status: status},
            function() {
                $(".alert").alert("Task status changed successfully");
                location.reload();
        })
        .error(function() { $(".alert").alert("Unable to delete the task");})
    });
});

function activateMenuSection(section){
    // Activates the current menu page
    $("#menu").children().each(function(){
        var li = $(this);
        if (li.attr('id') != section && li.attr('class') == 'active'){
            li.attr('class', '');
        }
        if (li.attr('id') == section){
            li.attr('class', 'active');
        }
    });
}