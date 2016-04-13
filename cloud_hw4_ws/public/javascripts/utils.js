function ChatClient(ws){
    if(ws){
        console.log('WS active');    
        this.socket = new WebSocket('ws://localhost:3001')
        this.subscribe = function(callback){
            this.socket.onmessage = function(event){
                callback(JSON.parse(event.data))
            }
        }
        this.publish = function(data){
            this.socket.send(JSON.stringify(data))
        }
    }
    else{
        this.subscribe = function(callback) {
            var longPoll = function(){
                $.ajax({
                    method: 'GET',
                    url: '/messages', 
                    success: function(data){
                        callback(data)
                    },
                    complete: function(){
                        longPoll()
                    },
                    timeout: 10000
                })
            }
            longPoll()
        }
        this.publish = function(data) {
            $.post('/messages', data)
        }
    }
}

function cleanConnections(){
    this.subscribe = null;
    this.publish = null;
    if(this.socket){this.socket.close();}
}