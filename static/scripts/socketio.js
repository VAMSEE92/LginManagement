document.addEventListener('DOMContentLoaded',()=>{
    var socket=io.connect("http://localhost:5000")
    let group;
//    socket.on('connect',()=>{
//        socket.send("I am connected");
//    });
//    Display incomming messages
    socket.on('message' ,data=>{
        const p=document.createElement('p');
        const br=document.createElement('br');
        const span_usr=document.createElement('span');
        span_usr.innerHTML=data.username;
        p.innerHTML=span_usr.outerHTML+br.outerHTML+data.msg+br.outerHTML;
        document.querySelector('#message_display').append(p);
    });

//    group selection
    document.querySelectorAll('.select-grp').forEach(p=>{
        p.onclick=()=>{
            let newGroup=p.innerHTML;
            if (newGroup==group){
                msg=`you are allready in ${group} group`
                printMsg(msg);
            }else{
             joinGrp(newGroup);
             group=newGroup;
             group=newGroup
            }
        }
    });
    //Leave Group
    function leaveGroup(group){
        socket.emit('leave',{'username':username, 'group':grup})
    }
    function joinGrp(group){
        socket.emit('join',{'username':username, 'group':group})
        //clear message
        document.querySelector('#message_display').innerHTML=''
    }

    //printing system messages
    function printMsg(msg){
        const p=document.createElement('p');
        p.innerHTML=msg;
        document.querySelector('#message_display').append(p);
    }
//    Send message
    document.querySelector('#send-message').onclick=()=>{
        socket.send({'msg':document.querySelector('#user-message').value,
            'username':username,'group':group
            });
    }

})