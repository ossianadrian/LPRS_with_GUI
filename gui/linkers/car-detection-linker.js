const { PythonShell } = require('python-shell')


function get_video() {

    //   var city = document.getElementById("city").value

    let options = { 
        mode: 'text', 
        pythonPath: '/home/ossi/anaconda3/bin/python3',
        pythonOptions: ['-u'], // get print results in real-time 
        scriptPath: '/home/ossi/Documents/licenta/graphical-user-interface/gui-app-lpr/engine', //If you are having python_test.py script in same folder, then it's optional. 
        args: ['/home/ossi/Documents/licenta/graphical-user-interface/gui-app-lpr/engine/test4k.mp4'] //An argument which can be accessed in the script using sys.argv[1] 
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


// get_video()

// let {PythonShell} = require('python-shell')

// get_video()

// function get_video() {

    
//     var options = { 
//         mode: 'text', 
//         pythonPath: '/home/ossi/anaconda3/bin/python3',
//         scriptPath: './', //If you are having python_test.py script in same folder, then it's optional. 
//     }; 
    
//     // var script = new python("test.py", options)

//     PythonShell.run('test.py', options, function (err, results) {
//         if (err) throw err;
//         console.log(results[0]);
//       });
    
    
//     // script.on('message', function (message){
//     //     console.log(message)
//     // })
    
// }