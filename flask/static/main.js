// Get the input field
var i = 0;
var input = document.getElementById("inputID");
var container = document.getElementById("container")
var rightArrow = document.getElementById("next")
var leftArrow = document.getElementById("previous")
var tripode = document.getElementById("tripode")
var viewer
var panorama
var ID


// Execute a function when the user releases a key on the keyboard
input.addEventListener("keyup", function(event) {
// Number 13 is the "Enter" key on the keyboard
if (event.keyCode === 13) {
    // Cancel the default action, if needed
    event.preventDefault();
    ID = input.value
    // Trigger the button element with a click
    fetch('http://localhost:5000/photos/' + ID, {
    method: 'GET',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    })
    .then(function(response) {
        response.json().then(data => {
            console.log(data);
            container.style.display = "none";
            rightArrow.style.display = "block";
            leftArrow.style.display = "block";
            tripode.style.display = "block";
            loadPicture(data, ID)
            console.log(data.length)
            rightArrow.onclick = () => {
                nextPicture(data, ID);
            }
            leftArrow.onclick = () => {
                previousPicture(data, ID);
            }
            tripode.onclick = () => {
                editTripode(data, ID);
            }

        });
    })
}
})



function loadPicture(names, ID) {
    var name = names[i];
    var path = 'static/dataset/' + ID + '/' + name;
    
    panorama = new PANOLENS.ImagePanorama(path);
    viewer = new PANOLENS.Viewer();

    viewer.add( panorama );
}

function nextPicture(names, ID) {
    if (i < names.length - 1) {
        i++;
    }
    else {
        i = 0
    }

    console.log(i)


    var name = names[i];
    var path = 'static/dataset/' + ID + '/' + name;

    viewer.remove( panorama );
    console.log(path)
    newpanorama = new PANOLENS.ImagePanorama( path );

    viewer.add( newpanorama );
    viewer.setPanorama( newpanorama );
    
    panorama = newpanorama

}

function previousPicture(names, ID) {
    if(i > 0) {
        i--;

    }

    else {
        i = names.length - 1
    }

    console.log(i)

    var name = names[i];
    var path = 'static/dataset/' + ID + '/' + name;

    viewer.remove( panorama );
    console.log(path)
    newpanorama = new PANOLENS.ImagePanorama( path );

    viewer.add( newpanorama );
    viewer.setPanorama( newpanorama );
    
    panorama = newpanorama    

}

function editTripode(names, ID) {

    // console.log(document.cookie)
    if (document.cookie == "") {
        console.log("no cookie")
        document.cookie = "file=" + JSON.stringify({filename: [names[i]], ID: ID});
    }
    else {
        cookievalue = document.cookie
        val = cookievalue.slice(5, cookievalue.length)
        val = JSON.parse(val)
        val["filename"].push(names[i])
        document.cookie = "file=" + JSON.stringify(val)
    }
    console.log("cookies added")
    window.location.replace("http://localhost:5000/paint");

        
    }