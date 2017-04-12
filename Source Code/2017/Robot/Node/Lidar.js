const RPLidar = require('rplidar');

const lidar = new RPLidar("/dev/ttyUSB0");

//var lidarArray = []

var restartLidar = true
lidar.on('data', data => {
        
        if (data == false){
            restartLidar = false
            if (restartLidar){
                lidar.stopScan()
                setTimeout(function(){lidar.scan();restartLidar = true},1000)
            }
            
            return
        }

        //lidarArray.push(data.distance)
        
        //var dataTwo = lidarArray[lidarArray.length - 1]
        //console.log(data)
        if (data.angle < 1 && data.possibleCorruption == false){
            //console.log("CLOSE TO CENER " + data.distance)
            var dist = data.distance * 2.54
            //console.log(data.distance * 2.54)
            if (dist < 2000 && data.distance != 0){
                
                console.log("DIDATHING")

                //lidar.stopScan()
                
                //setTimeout(function(){lidar.scan()},1000)
                //console.log("SOMETHING PEACEFUL, SOMETHING LIKE YOU SUCCESSFULLY PLACED YOUR HAND IN FRONT OF THE LIDAR. WE AT BEAGLEBONE ARE VERY HAPPY FOR YOU.")
            }
            
        }

    });


lidar.setErrorLevel(2)
//lidar.setDebugLevel(1)


lidar.init().then(async () => {

    let health = await lidar.getHealth();

    console.log('health: ', health);



    let info = await lidar.getInfo();

    console.log('info: ', info);

    
    //lidar.reset();
    lidar.scan()
    //await lidar.scan()
});