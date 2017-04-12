var zmq = require('zeromq')
  , sock = zmq.socket('sub');

sock.connect('tcp://127.0.0.1:5556');
sock.subscribe('Accelerometer');
//console.log('Subscriber connected to port 3000');

function hex2a(hexx) {
    var hex = hexx.toString();//force conversion
    var str = '';
    for (var i = 0; i < hex.length; i += 2)
        str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
    return str;
}

sock.on('message', function(topic, message) {
  console.log(topic.toString());
});