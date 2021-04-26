const { PythonShell } = require('python-shell')

var os = require('os');
var { dialog } = require('electron');

// load the video when user has chosen one
function loadTheVid() {

    // Read video file
    var input = document.getElementById("inputFile");
    filePath = input.files[0]
    var freader = new FileReader();
    freader.readAsDataURL(filePath);
    freader.onload = function(){
        document.getElementById("video").src = freader.result;
    }

    // enable upload button 
    document.getElementById("uploadBtn").disabled = false;

    // when loading video, reset progress bar to 0%
    document.getElementById("progressBarProcessing").setAttribute("aria-valuenow", "0")
    document.getElementById("progressBarProcessing").setAttribute("style", "width: 0%; background-color: 00d8ff; color: 18191A;")
    document.getElementById("progressBarProcessing").textContent = "0% Complete"
    // set info bar
    document.getElementById("list-of-results").innerHTML = '';
    document.getElementById("info-user").textContent = "This is where the informations about the processing status of your video are shown.";

}



function switchToDarkTheme() {
    document.getElementById('body').style = 'background-color: 18191A;'; //overflow: hidden;
    document.getElementById('info-user').style = 'background-color: 3A3B3C; color: E4E6EB; border-color: 3A3B3C';
    document.getElementById('footage-label').style = 'color: E4E6EB;';
    document.getElementById('results-label').style = 'color: E4E6EB;';
    document.getElementById('label-choose-file').style = 'background-color: 3A3B3C; color: B0B3B8; border-color: 3A3B3C';
    document.getElementById('inputFile').style = 'background-color: 3A3B3C; color: B0B3B8;';
    document.getElementById('uploadBtn').style = 'background-color: 3A3B3C; color: B0B3B8; border-color: 3A3B3C';
    document.getElementById('jumbotron').style = ' background-color: 3A3B3C;'
    document.getElementById('h1-title').style = ' color: E4E6EB'
    document.getElementById('p-title').style = ' color: B0B3B8'
    document.getElementById('p-title2').style = ' color: B0B3B8'
    document.getElementById('light-button').style = 'background-color: 000000; color: FFFFFF;'
    document.getElementById('dark-button').style = 'background-color: E4E6EB; color: 3A3B3C;'
    document.getElementById('badge1').style = 'background-color: 00d8ff; color: 18191A;'
    document.getElementById('badge2').style = 'background-color: 00d8ff; color: 18191A;'
    document.getElementById('badge3').style = 'background-color: 00d8ff; color: 18191A;'
    document.getElementById('badge4').style = 'background-color: 00d8ff; color: 18191A;'
    document.getElementById('progress-space').style = 'background-color: 3A3B3C; height: 38px;';
    document.getElementById('progressBarProcessing').style = 'background-color: 00d8ff; color: 18191A;';
}

function switchToLightTheme() {
    document.getElementById('body').style = 'background-color: FFFFFF;'; //overflow: hidden;
    document.getElementById('info-user').style = 'background-color: 00d8ff; color: 000000';
    document.getElementById('footage-label').style = 'color: 000000;';
    document.getElementById('results-label').style = 'color: 000000;';
    document.getElementById('label-choose-file').style = 'background-color: FFFFFF; color: 000000;';
    document.getElementById('inputFile').style = 'background-color: FFFFFF; color: FFFFFF;';
    document.getElementById('uploadBtn').style = 'background-color: FFFFFF; color: 000000;';
    document.getElementById('jumbotron').style = ' background-color: EEEEEE;'
    document.getElementById('h1-title').style = ' color: 000000'
    document.getElementById('p-title').style = ' color: 000000'
    document.getElementById('p-title2').style = ' color: 000000'
    document.getElementById('light-button').style = 'background-color: E4E6EB; color: 3A3B3C;'
    document.getElementById('dark-button').style = 'background-color: 000000; color: FFFFFF;'
    document.getElementById('badge1').style = 'background-color: 96F550; color: 000000;'
    document.getElementById('badge2').style = 'background-color: FE9000; color: FFFFFF;'
    document.getElementById('badge3').style = 'background-color: 19180A; color: FFFFFF;'
    document.getElementById('badge4').style = 'background-color: C3423F; color: FFFFFF;'
    document.getElementById('progress-space').style = 'background-color: EEEEEE; height: 38px;';
    document.getElementById('progressBarProcessing').style = 'background-color: FFFFFF; color: FFFFFF;';
}

function process_video() {

    document.getElementById('uploadBtn').disabled = true

    var filePath = document.getElementById('inputFile').files[0].path

    var curr_loc = window.location.pathname;
    var script_path = curr_loc.substring(0, curr_loc.lastIndexOf('/'));
    script_path = script_path.substring(0, script_path.lastIndexOf('/'));
    script_path = script_path + "/engine"

    let options = {
        mode: 'text',
        pythonOptions: ['-u'], // get print results in real-time 
        scriptPath: script_path,
        args: [filePath] //An argument which can be accessed in the script using sys.argv[1] 
    };

    var script = new PythonShell('speed_calculation_and_LPR.py', options)

    var carImagePaths = [];
    var carTexts = [];
    var carIndex = [];

    script.on('message', function (message) {
        if (message.includes("[Info]")) {
            document.getElementById("info-user").textContent = message.substr(7);
        }
        else if (message.includes("[Progress]")) {
            var progress = message.substr(11)
            //update progress bar
            document.getElementById("progressBarProcessing").setAttribute("aria-valuenow", progress);
            document.getElementById("progressBarProcessing").setAttribute("style", "width: " + progress + "%; background-color: 00d8ff; color: 18191A;");
            document.getElementById("progressBarProcessing").textContent = progress + "% Complete";
        }
        else if (message.includes("[Vehicle]")) {
            carTexts.push(message.substr(10));
        }
        else if (message.includes("[Index]")) {
            carIndex.push(message.substr(8));
        }
        else if (message.includes("[Img path]")) {
            carImagePaths.push(message.substr(10));
        }
        else if (message.includes("Finished")) {
            showResultsAsCards(carIndex, carImagePaths, carTexts);
            // showResultedVideo();
            document.getElementById("info-user").textContent = "The video processing ended with success! The results are showing below.";
        }
    })


}

function showResultedVideo() {
    var curr_loc = window.location.pathname;
    var video_path = curr_loc.substring(0, curr_loc.lastIndexOf('/'));
    video_path = video_path.substring(0, video_path.lastIndexOf('/'));
    video_path = video_path + "/engine/outputVideo.mp4"

    document.getElementById('videoFrame').setAttribute("src", video_path)
    var video = document.getElementById('video');
    video.load();
}


function showResultsAsCards(carIndex, carImagePaths, carTexts) {
    /*
        What I want to create
        <div class="card">
          <img src="/home/ossi/Documents/licenta/graphical-user-interface/gui-app-lpr/engine/exported/resulted_image_with_LPR0.png" class="card-img-top" alt="Car image">
          <div class="card-body">
            <h5 class="card-title">Card title that wraps to a new line</h5>
            <p class="card-text">This is a longer card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.</p>
          </div>
        </div>
    */

    var resultsDiv = document.getElementById("list-of-results");
    var i;
    for (i = 0; i < carIndex.length; i++) {

        //create card element
        var cardElement = document.createElement("div");
        cardElement.setAttribute('class', "card")
        cardElement.style = 'background-color: 3A3B3C; color: E4E6EB; border-color: 18191A'
        //create image element 
        var imgEl = document.createElement("img");
        imgEl.setAttribute('class', "card-img-top");
        imgEl.setAttribute('src', carImagePaths[i]);
        imgEl.setAttribute('alt', "Car number " + carIndex[i])

        var cardBodyDiv = document.createElement("div");
        cardBodyDiv.setAttribute('class', "card-body");

        var cardTitleH5 = document.createElement("h5");
        cardTitleH5.setAttribute('class', "card-title");
        cardTitleH5.textContent = "Car #" + carIndex[i];

        var cardTextP = document.createElement("p");
        cardTextP.setAttribute('class', "card-text");
        cardTextP.textContent = carTexts[i];

        //append all elements
        cardElement.appendChild(imgEl);

        cardBodyDiv.appendChild(cardTitleH5);
        cardBodyDiv.appendChild(cardTextP);
        cardElement.appendChild(cardBodyDiv);

        //append the created structure to the list-of-results div
        resultsDiv.appendChild(cardElement);

    }

}
