var canvas0, canvas1, canvas2;
var canvas_wrapper

var lastX, lastY;
var recentX, recentY;
var ctx0, ctx1, ctx2;
var dragmode = false;
var rect_temp_finished = false;
var label_dropdown;
var baseimg
var index_label
var savebtn


var temp_rect;

var MOVE_PIXEL_THRESHOLD = 20;
var SELECT_BUFFER = 30;

var finished_rects = [];
var selected_rects_index_arr = [];

var SELECTED_RECT_STROKE_COLOR = "#1bfc07"
var DEFAULT_RECT_STROKE_COLOR = "#ff1616"


var current_img_index = 0;
var dataset_id = 0;
var total_image_number = 0;





var SERVER_BASE_ADDR = "https://chadrick-kwag.net/labeldata"


var user_label_result = {}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            console.log(cookies[i])
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        // if (!(csrfSafeMethod(settings.type) && sameOrigin(settings.url))) {
        //     // if (!csrfSafeMethod(settings.type) && !this.crossDomain){
        //     // Send the token to same-origin, relative URLs only.
        //     // Send the token only if the method warrants CSRF protection
        //     // Using the CSRFToken value acquired earlier
        //     // xhr.setRequestHeader("X-CSRFToken", "CcVK5u7uUKZAxa3is9ROgd8o9oX31rLBFc61hePIWgc5WxcerxbMJWizz86Qldok");
        //     xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        // }
        // console.log("adding ",getCookie('csrftoken'))
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    crossDomain: true,
    xhrFields: {
        withCredentials: true
    }
    
});



window.onload = function() {

    dataset_id =  passed_on_dsid
    console.log("setting dataset_id to ",dataset_id)

    // communicate with server

    console.log("csrftoken", csrftoken)


    // get total_image number first
    fetch_total_image_number()


    canvas_wrapper = document.getElementById("canvas_wrapper")
    canvas0 = document.getElementById("canvas0")
    canvas1 = document.getElementById("canvas1")
    canvas2 = document.getElementById("canvas2")

    savebtn = document.getElementById("savebutton")

    index_label = document.getElementById("image_index")
    

    ctx0 = canvas0.getContext('2d')
    ctx1 = canvas1.getContext('2d')
    ctx2 = canvas2.getContext('2d')
    label_dropdown = document.getElementById("labeldropdown")


    

    $("#dsinfo").html("dataset id = " + dataset_id)

    

    baseimg = document.getElementById('bgimage')
    baseimg.onload = function() {
        console.log("on image load")
        canvas0.width = baseimg.width
        canvas0.height = baseimg.height

        canvas1.width = baseimg.width
        canvas1.height = baseimg.height

        canvas2.width = baseimg.width
        canvas2.height = baseimg.height



        ctx0.drawImage(baseimg, 0, 0)

        console.log(baseimg.width, baseimg.height)

        canvas_wrapper.style.minHeight = canvas0.height
        canvas_wrapper.style.width = canvas0.width

        update_index_label()
        finished_rects = []
        // update finished_rects to the user_label_result
        if(user_label_result[current_img_index]!= null){
            finished_rects = user_label_result[current_img_index]
        }
        
        console.log("on image load: newly populated finished_rects",finished_rects)

        redraw_all_finished_rects()

    }

    // fetch save_progress and put it in out variable




    baseimg.src = SERVER_BASE_ADDR + "/web/" + dataset_id + "/img/" + current_img_index



    ctx1.strokeStyle = DEFAULT_RECT_STROKE_COLOR
    ctx1.lineWidth = 10


    canvas2.addEventListener('mousedown', function(evt) {

        // console.log("evt.offsetX",evt.offsetX);
        console.log("second param", evt.pageX - canvas2.offsetLeft);
        lastX = evt.offsetX || (evt.pageX - canvas2.offsetLeft);
        lastY = evt.offsetY || (evt.pageY - canvas2.offsetTop);
        // console.log("lastX:",lastX," lastY:",lastY);



    }, false);

    canvas2.addEventListener('mousemove', function(evt) {


        if (evt.buttons == 1) {
            var currX = evt.offsetX;
            var currY = evt.offsetY;

            recentX = currX;
            recentY = currY;

            // console.log(evt)

            if (dragmode == false && (Math.abs(currX - lastX) > MOVE_PIXEL_THRESHOLD || Math.abs(currY - lastY) > MOVE_PIXEL_THRESHOLD)) {
                dragmode = true;
            }


            if (dragmode) {

                // clean first
                // console.log("canvas2.width=",canvas2.width,"canvas2.height=",canvas2.height);
                erase_temp_rect()


                ctx2.beginPath();
                temp_rect = [lastX, lastY, currX - lastX, currY - lastY];
                ctx2.rect(lastX, lastY, currX - lastX, currY - lastY);
                ctx2.stroke();
                ctx2.closePath();
            }
        }
    });

    window.addEventListener('mouseup',function(evt){

        console.log("window mouseup listener")

        if(dragmode){
            dragmode = false;
            rect_temp_finished = true;
            console.log("calling show_label_dropdown_autocalculate")

            show_label_dropdown_autocalculate();
        }

    })

    canvas2.addEventListener('mouseup', function(evt) {


        console.log("canvas2 mouseup listener")
        // console.log("inside mouseup",dragmode);
        if (dragmode) {
            // console.log("inside dragmode true")
            dragmode = false;
            rect_temp_finished = true;


            show_label_dropdown(evt.offsetX, evt.offsetY)
        } else {


            if (rect_temp_finished) {
                // this case is when a temp_rect is drawn.

                // erase rect_temp
                erase_temp_rect()
                hide_label_dropdown()
            } else {
                // this is when we normally click somewhere


                // check if it has selected one of the finished rects.
                var retval = check_if_selected_finished_rect(evt.offsetX, evt.offsetY)
                if (retval == null) {
                    // we really have clicked nowhere significant.
                    console.log("no rect is selected");
                    clear_all_selected()
                } else {
                    // retval contains the index of the selected rect

                    console.log("some rect has been selected");
                    toggle_push_to_selected_rects(retval)

                    redraw_all_finished_rects()
                }
            }
        }

    });


    savebtn.onclick = function() {
        console.log("savebtn clicked")

        update_user_label_result()

        // var xhttp = new XMLHttpRequest()
        // xhttp.onreadystatechange = function() {
        //     if (this.readyState == 4 && this.status == 200) {
        //         console.log("upload success")

        //     }
        //     else{
        //      console.log("upload error",this.readyState,this.status)
        //     }
        // }

        var sendaddr = SERVER_BASE_ADDR + "/web/save"
        console.log("sending to ", sendaddr)
        // xhttp.open("POST", sendaddr)
        // xhttp.setRequestHeader('Content-Type', 'application/json');
        var sendjson = {}
        sendjson.dataset_id = dataset_id
        sendjson.data = user_label_result
        // console.log("sending",sendjson)
        // xhttp.send(JSON.stringify(sendjson))


        $.ajax({
            url: sendaddr,
            type: 'post',

            headers: {
                "X-CSRFToken": csrftoken
            },
            // crossDomain: true,
            xhrFields: {
                withCredentials: true
            },
            data: JSON.stringify(sendjson),
            dataType: 'json',
            success: function(data) {
                console.log("success", data)

            }
        })

    }

    fetch_saved_progress()

}


window.addEventListener("keydown", function(evt) {

    console.log(evt)

    if (evt.key == "PageUp") {
        evt.preventDefault()

        update_user_label_result()

        current_img_index++
        if (current_img_index >= total_image_number) {
            current_img_index = total_image_number - 1
            // and do nothing.
        } else {
            reload_imgsrc()
        }


    } else if (evt.key == "PageDown") {
        evt.preventDefault()

        update_user_label_result()
        current_img_index--
        if (current_img_index < 0) {
            // this is invalid
            current_img_index = 0
            // do nothing.

        } else {
            reload_imgsrc()
        }

    } else if (evt.key == "Enter") {
        if (rect_temp_finished) {
            rect_temp_finished = false;
            draw_temp_rect();
            erase_temp_rect()
            add_rect_to_savedlist();
            hide_label_dropdown()
        }
    } else if (evt.key == 'u') {
        savebtn.click()
    } else if (evt.key == "Delete") {
        // if there are any selected rects, remove them from finished_rect list
        // and then redraw the whole finished rects

        // copy finished_rect that are not included in selected_rects
        var temp_finished_rect_arr = []
        console.log("selected_rects_index_arr", selected_rects_index_arr)
        console.log("finished_rects", finished_rects)
        for (i = 0; i < finished_rects.length; i++) {
            if (!selected_rects_index_arr.includes(i)) {
                console.log(i, "is not included in selected_rects")
                temp_finished_rect_arr.push(finished_rects[i])
            } else {
                console.log(i, "is included in selected rects")
            }
        }

        console.log("temparr", temp_finished_rect_arr)

        // clear selected_rects
        selected_rects_index_arr = []
        // set the finished_rects to the temparr
        finished_rects = temp_finished_rect_arr

        console.log("after finished rects", finished_rects)

        //redraw
        redraw_all_finished_rects()
    }

})




function draw_temp_rect() {

    draw_unselected_rect([temp_rect[0], temp_rect[1], temp_rect[2], temp_rect[3]], label_dropdown.value)

    // ctx1.beginPath();
    // ctx1.rect(temp_rect[0], temp_rect[1], temp_rect[2], temp_rect[3]);
    // ctx1.stroke();
    // ctx1.closePath();

}

function erase_temp_rect() {
    ctx2.clearRect(0, 0, canvas2.width, canvas2.height);
}

function add_rect_to_savedlist() {
    var tempjson = {}
    tempjson.startX = temp_rect[0]
    tempjson.startY = temp_rect[1]
    tempjson.widthX = temp_rect[2]
    tempjson.widthY = temp_rect[3]
    tempjson.label = label_dropdown.value

    finished_rects.push(tempjson)
    console.log(finished_rects)
}


function check_if_selected_finished_rect(pointX, pointY) {
    // return true if the given x,y is inside the bigger rect but not in smaller rect
    // check on all finished_rects
    for (i = 0; i < finished_rects.length; i++) {
        var picked_rect = finished_rects[i];
        console.log("picked_rect", picked_rect)
        var retval = is_selecting_finished_rect(pointX, pointY, picked_rect.startX, picked_rect.startY, picked_rect.widthX, picked_rect.widthY);
        if (retval) {
            console.log("selected rect:", picked_rect);
            return i;
        }
    }

    return null;
}

function is_selecting_finished_rect(px, py, x, y, w, h) {

    console.log("is_selecting_finished_rect input params:", px, py, x, y, w, h)
    var big_rect_param = [x - SELECT_BUFFER / 2, y - SELECT_BUFFER / 2, w + SELECT_BUFFER, h + SELECT_BUFFER]
    var small_rect_param = [x + SELECT_BUFFER / 2, y + SELECT_BUFFER / 2, w - SELECT_BUFFER, h - SELECT_BUFFER]

    console.log(big_rect_param)
    console.log("enclosed by bigger", is_enclosed_by_rect_2(px, py, big_rect_param))
    console.log("enclosed by smaller", is_enclosed_by_rect_2(px, py, small_rect_param))

    if (is_enclosed_by_rect_2(px, py, big_rect_param) == true && is_enclosed_by_rect_2(px, py, small_rect_param) == false) {
        return true;
    } else {
        return false;
    }

}


function is_enclosed_by_rect_2(pX, pY, param_array) {
    console.log(param_array)
    return is_enclosed_by_rect(pX, pY, param_array[0], param_array[1], param_array[2], param_array[3])
}


function is_enclosed_by_rect(pX, pY, x, y, w, h) {
    // calculate x1,x2,y1,y2
    // where x1<x2 and y1<y2



    var x1 = x;
    var x2 = x + w;
    var y1 = y;
    var y2 = y + h;

    var temp;
    if (x1 > x2) {
        temp = x1;
        x1 = x2;
        x2 = temp;
    }

    if (y1 > y2) {
        temp = y1;
        y1 = y2;
        y2 = temp;
    }

    console.log(pX, pY, x1, y1, x2, y2)

    if (pX > x1 && pX < x2 && pY > y1 && pY < y2) {
        return true;
    } else {
        return false;
    }
}

function redraw_all_finished_rects() {

    console.log("calling redraw_all_finished_rects")

    // draw non selected first

    // generate non-selected index array
    non_selected_index_arr = []
    for (i = 0; i < finished_rects.length; i++) {
        if (!selected_rects_index_arr.includes(i)) {

            non_selected_index_arr.push(i)
        }
    }

    console.log("non_selected_index_arr:", non_selected_index_arr)
    // clear the whole canvas
    clear_whole_drawing_canvas()

    // for non selected, draw them
    for (i = 0; i < non_selected_index_arr.length; i++) {
        var iterateitem = finished_rects[non_selected_index_arr[i]]

        draw_unselected_rect([iterateitem.startX, iterateitem.startY, iterateitem.widthX, iterateitem.widthY],iterateitem.label)
    }

    // draw selected rects
    for (i = 0; i < selected_rects_index_arr.length; i++) {
        var iterateitem = finished_rects[selected_rects_index_arr[i]]
        draw_selected_rect([iterateitem.startX, iterateitem.startY, iterateitem.widthX, iterateitem.widthY],iterateitem.label)
    }




}

function show_label_dropdown(x, y) {
    console.log("label dropdown show", x, y)
    label_dropdown.style.display = "block"
    label_dropdown.style.left = x + "px" // for firefox. for some reason adding the 'px' makes it work.
    label_dropdown.style.top = y + "px"

    console.log("label x,y whaat", label_dropdown.style.left, label_dropdown.style.top)
    console.log(label_dropdown)

}

function hide_label_dropdown() {
    label_dropdown.style.display = "none"
}

function clear_all_selected() {
    // empty the selected array
    selected_rects_index_arr = []

    // redraw every finished rects
    redraw_all_finished_rects()
}

function draw_unselected_rect(rectparam,labelname) {

    ctx1.strokeStyle = DEFAULT_RECT_STROKE_COLOR;
    ctx1.lineWidth = 5
    ctx1.beginPath()
    ctx1.rect(rectparam[0], rectparam[1], rectparam[2], rectparam[3]);
    ctx1.stroke();
    ctx1.closePath();

    // testing adding label
    console.log("creating label textbox")
    var newlabel = document.createElement("Label")
    // newlabel.setAttribute("style","backgroud-color:white;")
    newlabel.setAttribute("class","datalabel")
    newlabel.innerHTML = labelname
    newlabel.style.left = rectparam[0]+"px"
    newlabel.style.top = rectparam[1]+"px"
    newlabel.style.backgroundColor = "white"
    newlabel.style.position="absolute"

    console.log(newlabel)

    // label_dropdown.style.display = "block"
    // label_dropdown.style.left = x + "px" // for firefox. for some reason adding the 'px' makes it work.
    // label_dropdown.style.top = y + "px"
    $("#canvas_wrapper").append(newlabel)




}

function draw_unselected_rect_withlabel(rectparam,labelname) {

    ctx1.strokeStyle = DEFAULT_RECT_STROKE_COLOR;
    ctx1.lineWidth = 5
    ctx1.beginPath()
    ctx1.rect(rectparam[0], rectparam[1], rectparam[2], rectparam[3]);
    ctx1.stroke();
    ctx1.closePath();


    

    


}

function draw_selected_rect(rectparam,labelname) {
    ctx1.strokeStyle = SELECTED_RECT_STROKE_COLOR
    ctx1.lineWidth = 5
    ctx1.beginPath()
    ctx1.rect(rectparam[0], rectparam[1], rectparam[2], rectparam[3]);
    ctx1.stroke();
    ctx1.closePath();


    // testing adding label
    console.log("creating label textbox")
    var newlabel = document.createElement("Label")
    // newlabel.setAttribute("style","backgroud-color:white;")
    newlabel.setAttribute("class","datalabel")
    newlabel.innerHTML = labelname
    newlabel.style.left = rectparam[0]+"px"
    newlabel.style.top = rectparam[1]+"px"
    newlabel.style.backgroundColor = "white"
    newlabel.style.position="absolute"

    console.log(newlabel)

    // label_dropdown.style.display = "block"
    // label_dropdown.style.left = x + "px" // for firefox. for some reason adding the 'px' makes it work.
    // label_dropdown.style.top = y + "px"
    $("#canvas_wrapper").append(newlabel)

}

function toggle_push_to_selected_rects(request_index) {
    // if already in the selectred_rects array, remove from it. and vise versa

    if (selected_rects_index_arr.includes(request_index)) {
        // if it contains it, then remove it.
        var index = selected_rects_index_arr.indexOf(request_index)
        selected_rects_index_arr.splice(index, 1)
    } else {
        // simply add it to the selected array
        selected_rects_index_arr.push(request_index)
    }

}


function fetch_total_image_number() {
    // var xhttp = new XMLHttpRequest()
    // xhttp.onreadystatechange = function() {
    //     if (this.readyState == 4 && this.status == 200) {
    //         console.log("response:", JSON.parse(this.responseText))
    //         total_image_number = JSON.parse(this.responseText).number_of_images
    //     }
    // }

    var sendaddr = SERVER_BASE_ADDR + "/web/" + dataset_id + "/info"
    // console.log("sending to ", sendaddr)
    // xhttp.open("POST", sendaddr)
    // xhttp.send()

    // $.post(sendaddr,{},function(data,status){
    //     console.log("info response",data,status)
    // })
    $.ajax({
        url: sendaddr,
        type: 'get',

        // headers: {
        //     "X-CSRFToken": csrftoken
        // },
        xhrFields: {
            withCredentials: true
        },
        dataType: 'json',
        success: function(data) {
            console.log("whwhahaht")
            console.log("ajax success", data)
            total_image_number = data.number_of_images

        }
    })
}

function reload_imgsrc() {
    // baseimg.src = SERVER_BASE_ADDR + "/web/" + dataset_id + "/img/" + current_img_index
    $("#bgimage").attr("src",SERVER_BASE_ADDR + "/web/" + dataset_id + "/img/" + current_img_index)
}


function update_index_label() {
    console.log("inside update_index_label", current_img_index, total_image_number)

    

    $("#image_index").html((current_img_index+1) + "/" + total_image_number)
}

function update_user_label_result() {
    // insert to the user_label_result
    console.log("update_user_label_result occured")
    
    user_label_result[current_img_index] = finished_rects

    console.log(user_label_result)
}

function fetch_saved_progress(){
    var sendaddr = SERVER_BASE_ADDR + "/progress"
    var sendjson = {}
    sendjson.dataset_id = dataset_id
    $.ajax({
            url: sendaddr,
            type: 'post',

            headers: {
                "X-CSRFToken": csrftoken
            },
            // crossDomain: true,
            // xhrFields: {
            //     withCredentials: true
            // },
            data: JSON.stringify(sendjson),
            dataType: 'json',
            success: function(data) {
                console.log("fetched save progress data", data)
                datainjson = JSON.parse(data)
                user_label_result = datainjson.data

                console.log("populated user_label_result",user_label_result)

                // get current index and insert it
                fetched_current_rects = user_label_result[current_img_index]
                console.log("fetched success: current index rects",fetched_current_rects)

                finished_rects=fetched_current_rects

                //draw the finished_rects
                redraw_all_finished_rects() 



            }
        })
}

function show_label_dropdown_autocalculate(){


    // calculate the coordinate to trigger show_label_dropdown function
    // use startX,y, recentX,Y

    better_x = closer_to_center_of_img(lastX, recentX, baseimg.width )
    better_y = closer_to_center_of_img(lastY, recentY, baseimg.height)

    console.log(lastX,lastY, recentX, recentY)
    console.log("chose ",better_x,better_y)

    show_label_dropdown(better_x,better_y)
    
    
}

function closer_to_center_of_img(a,b,l){
    // a,b: the param that are competing
    // l: the critea of comparison. the one that is closer to the half value of l wins

    if(a==b){
        return a
    }

    delta_a = Math.abs(l/2-a)
    delta_b = Math.abs(l/2-b)

    if(delta_a>delta_b){
        return b;
    }
    else{
        return a;
    }
}

function clear_whole_drawing_canvas(){
    ctx1.clearRect(0, 0, canvas1.width, canvas1.height);
    // and also remove all datalabels
    $(".datalabel").remove()    
}

