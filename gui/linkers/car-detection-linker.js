const { PythonShell } = require('python-shell')

var os = require('os');
var {dialog} = require('electron');

// TODO: sa fac sa pot alege din src-urile de video. Sa il pot alege si pe ala generat. snwpmau sa il pun automat dupa ce il exporteaza


// load the video when user has browsed
function loadTheVid(){

    var filePath = document.getElementById('inputFile').files[0].path
    document.getElementById('videoFrame').setAttribute("src",filePath)
    var video = document.getElementById('video');
    video.load();

}

function get_video() {

    //   var city = document.getElementById("city").value  
    
    var filePath = document.getElementById('inputFile').files[0].path

    let options = { 
        mode: 'text', 
        pythonPath: '/home/ossi/anaconda3/bin/python3',
        pythonOptions: ['-u'], // get print results in real-time 
        scriptPath: '/home/ossi/Documents/licenta/graphical-user-interface/gui-app-lpr/engine', //If you are having python_test.py script in same folder, then it's optional. 
        args: [filePath] //An argument which can be accessed in the script using sys.argv[1] 
    }; 
    
    var script = new PythonShell('speed_calculation_and_LPR.py', options)

    script.on('message', function (message){
        console.log(message)
    })
    

    


    //   pyshell.on('message', function(message) {
    //     swal(message);
    //   })
    //   document.getElementById("city").value = "";
}

