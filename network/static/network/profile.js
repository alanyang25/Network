document.addEventListener("DOMContentLoaded", function() {
    let btn = document.querySelector("#unfollowbtn")
    
    // Cannot set property 'onmouseover' of null
    if(btn !== null) {
        btn.onmouseover = function() {
            btn.value = "Unfollow"
            btn.className = "btn btn-danger rounded-pill"
        }
        btn.onmouseout = function() {
            btn.value = "Following"
            btn.className = "btn btn-primary rounded-pill"
        }
    }
})