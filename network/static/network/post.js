document.addEventListener("DOMContentLoaded", function() {

    document.querySelectorAll("#editbtn").forEach(function(editbtn) {
        editbtn.onclick = function() {
            postid = editbtn.dataset.postid;
            console.log(postid)
            editbtn.style.display = 'none';
            content = document.querySelector(`#content${editbtn.dataset.postid}`);
            content.innerHTML = `
                <form id="editform" style="white-space:nowrap;">
                    <div class="form-group" style="white-space:nowrap;">
                        <textarea class="form-control" rows="3" cols="50" id="editedpost">${content.innerHTML}</textarea>
                        <button type="submit" class="btn btn-secondary btn-sm rounded-pill float-right">Save</button>
                    </div>
                </form>`

            document.querySelector("#editform").onsubmit = function() {
                const editedpost = document.querySelector("#editedpost").value;
                const post_id = editbtn.dataset.postid;
                console.log(editedpost)

                fetch('/post', {
                    method: "PUT", 
                    body: JSON.stringify({editedpost, post_id})
                })
                .then(response => response.json())
                .then(result => {
                    content.innerHTML = editedpost;
                    editbtn.style.display = 'block'
                })
                .catch(err => {
                    console.log(err)
                })
                return false;
            }
        }
    });

    document.querySelectorAll(".likebtn").forEach(function(likebtn) {
        likebtn.onclick = function() {
            fetch('/post', {
                method: 'PUT',
                body: JSON.stringify({clicked: true, post_id: likebtn.dataset.postid})
            })
            .then(response => response.json())
            .then(result => {
                let likes_count = document.querySelector(`#likes${likebtn.dataset.postid}`);

                if(parseInt(likes_count.innerHTML, 10) > parseInt(result.likes_number, 10)){
                    likebtn.innerHTML = "<i class='far fa-heart'></i>"
                }else if(parseInt(likes_count.innerHTML, 10) < parseInt(result.likes_number, 10)){
                    likebtn.innerHTML = "<div style='color: red;'><i class='fa fa-heart'></i></div>"
                }

                document.querySelector(`#likes${likebtn.dataset.postid}`).innerHTML = result.likes_number;
            })
            .catch(err => {
                console.log(err)
            })
            return false;
        }
    });
    
});