#pragma downcast

public var lidarDistance :int = 100;

var currentAngle = 0;

var frameCount = 0;
var lidarCount = 0;
var lidarPerFrame = 120;
var lidarArray = new Array();
var debugLevel = 0;
var sphere :GameObject;
var debugRealLocation :GameObject;
var debugRobotLocation :GameObject;

function Start () {
    for (var i = 0; i < 360; i++){
        lidarArray.Add(0);
    }
    //print(lidarArray.length);

    //print(generateShapeChecksum([new point(0,0),new point(0,1), new point(1,1)]));
}

function Update () {
    frameCount++;
    //if (frameCount % 400 == 0){
    //for (var angle = 0; angle < 360; angle++){
    if (frameCount % 60 == 0){
        lidarCount += lidarPerFrame;
        robotDecide(lidarArray);
    }else{
        for (var i = 0; i < lidarPerFrame; i++){
            getLidarValueForAngle(lidarCount % 360);
        }
    }
    //run calculations
    if (frameCount > 120){
        move(60,60);
    }
        //}
    //}
}

function radians(deg){
    var degreesToMult: float = deg;
    return degreesToMult * Mathf.Deg2Rad;
}
function degrees(rad){
    var radToMult: float = rad;
    return radToMult * Mathf.Rad2Deg;
}
function getLidarValueForAngle(angle){
    lidarCount++;
    var sin: float = Mathf.Sin(radians(angle));
    var cos: float = Mathf.Cos(radians(angle));
    var angleToCast: Vector3 = transform.TransformDirection(Vector3(sin,0,cos));
    var hit: RaycastHit;
    if (Physics.Raycast(transform.position, angleToCast, hit, lidarDistance)){
        //print("There is something in front of the object!");
        //print(hit.distance);
        lidarArray[lidarCount % 360] = hit.distance;
        if (debugLevel > 2){
            Debug.DrawLine(transform.position, hit.point, Color.blue);
        }
    }
    if (debugLevel > 3){
        Debug.DrawRay (transform.position, angleToCast, Color.green);
    }
    //print(radians(360));
}

function returnVector3Angle(angle){
    var sin: float = Mathf.Sin(radians(angle));
    var cos: float = Mathf.Cos(radians(angle));
    var angleToCast: Vector3 = transform.TransformDirection(Vector3(sin,0,cos));
    return angleToCast;
}

function move(left,right){
    var rightMotor :int = right;
    var leftMotor :int = left;
    var difference :float = leftMotor - rightMotor;
    var movementSpeed :float = (leftMotor + rightMotor) / 2;
    //difference being positive is a right turn
    //AKA if RightMotor is 100, and leftMotor is -100, the difference is -200, so it goes left
    //if RightMotor is -100, and leftMotor is 100, the difference is 200, so it goes right
    var turn :float = difference / 200;
    //print(turn);
    var movement :float = movementSpeed / 10000;
    transform.Rotate(Vector3.up * turn);
    currentAngle = (currentAngle + turn) % 360;
    transform.position = transform.position + returnVector3Angle(currentAngle) * movement;
}


var arrayOfPoints = new Array();
var samePointDifference = 0.05;

class point{
    var x;
    var y;
    var uncertainty;
    function point(x,y){
        this.x = x;
        this.y = y;
        this.uncertainty = 0; // Note it is 0 by default
    }
    }

private var RobotLocation :point = new point(0,0);

function pointIsInArray(point){
    //print(arrayOfPoints.length);
    if(!(arrayOfPoints.length > 0)){
        //print("FALSE");
        return -2;
    }
    for (var i = 0; i < arrayOfPoints.length; i++){
        var toCompare = arrayOfPoints[i];
        if ((Mathf.Abs(toCompare.x - point.x) < samePointDifference) && (Mathf.Abs(toCompare.y - point.y) < samePointDifference)){
            //print("TRUE");
            return i;
        }
    }
    return -2;
}


class cornerBatch{
    var cornerBatches;

    function cornerBatch(){
        this.cornerBatches = new Array();
    }

}

private var batchList :cornerBatch = new cornerBatch();

function batchCorners(spottedCornerArray){
    for (var i = batchList.cornerBatches.length; i <= spottedCornerArray.length; i++){
        batchList.cornerBatches.Add(new Array());
    }

    var newArray = new Array();
    for (var j = 0; j < spottedCornerArray.length; j++){
        newArray.Add(pointIsInArray(spottedCornerArray[j]));
    }
    //print(newArray.toString());

    var BatchList = batchList.cornerBatches[spottedCornerArray.length];
    for (var k = 0; k < BatchList.length; k++){
        if (BatchList[k] == newArray.toString()){
            //print("Seen this corner batch before");
            return;
        }
    }

    batchList.cornerBatches[spottedCornerArray.length].Add(newArray.toString());

    //print("GOT THIS FAR");

}

function generateShapeChecksum(cornerArray){
    //var dxArray = new Array();
    //var dyArray = new Array();
    var hypotenuseLength = 0f;

    for (var i = 0; i < cornerArray.length; i++){
        //dxArray.Add(cornerArray[i].x - cornerArray[(i + 1) % cornerArray.length].x);
        //dyArray.Add(cornerArray[i].y - cornerArray[(i + 1) % cornerArray.length].y);
        var opp = Mathf.Pow(cornerArray[i].y - cornerArray[(i + 1) % cornerArray.length].y, 2);
        var adj = Mathf.Pow(cornerArray[i].x - cornerArray[(i + 1) % cornerArray.length].x, 2);
        hypotenuseLength += Mathf.Pow(opp + adj, 0.5);
    }
    
    return hypotenuseLength;
}

function generateShapeChecksumFromPointIds(cornerIdArray){
    var cornerArray = new Array();
    for (var i = 0; i < cornerIdArray.length; i++){
        //print(cornerIdArray[i]);
        var cornerId = parseInt(cornerIdArray[i]);
        cornerArray.Add(arrayOfPoints[cornerId]);
    }
    return generateShapeChecksum(cornerArray);
}

function returnCornerArrayFromPointsIds(cornerIdArray){
    var cornerArray = new Array();
    //print(cornerIdArray.length);
    for (var i = 0; i < cornerIdArray.length; i++){
        //print(cornerIdArray[i]);
        var cornerId = cornerIdArray[i];
        //print(arrayOfPoints[cornerId]);
        //print(arrayOfPoints[cornerId].x);
        cornerArray.Add(arrayOfPoints[parseInt(cornerId)]);
        //print(cornerIdArray[i]);
    }
    return cornerArray;
}

//if they batch return the batch ID
//If they don't batch, then return an invalid batch ID
//make a checksum for each shape, if the checksums are equal then further compare
function checkIfCornersBatch(cornerArray){
    if (batchList.cornerBatches.length > cornerArray.length){
        var batches = batchList.cornerBatches[cornerArray.length];
        var checksum = generateShapeChecksum(cornerArray);
        for (var i = 0; i < batches.length; i++){
            //all the corner batch IDs
            var batchCorners = batches[i].Split(","[0]);
            /*for (var x = 0; x < batchCorners.length; x++){
                print("got here");

            }*/
            var toCompare = generateShapeChecksumFromPointIds(batchCorners);
            if (Mathf.Abs(checksum - toCompare) < 0.5){
                //print("Same corners. Batch recognised.");
                return i;
            }
        }
        //print("NEW BATCH");
    }
    else{
        return -1;
    }
    return -1;
}

function calculateAngleFromRelative(arrayOfBasePoints, readingArray){
    var longestSideArray = new Array();
    var longestSideLength = 0f;
    for (var i = 0; i < arrayOfBasePoints.length; i++){
        var pointA = arrayOfBasePoints[i];
        var pointB = arrayOfBasePoints[(i + 1) % arrayOfBasePoints.length];
        /*print("POINT DATA");
        print("POINT A");
        print(pointA.x);
        print(pointA.y);
        print("POINT B");
        print(pointB.x);
        print(pointB.y);
        print("----------");*/
        var rise = pointB.y - pointA.y;
        var run = pointB.x - pointA.x;
        var length = Mathf.Sqrt(Mathf.Pow(rise,2) + Mathf.Pow(run,2));
        if (length > longestSideLength){
            /*print("NEW LONGEST LENGTH");
            print(run);
            print(rise);
            print("------------------");*/
            longestSideLength = length;
            longestSideArray = new Array();
            longestSideArray.Add(pointA);
            longestSideArray.Add(pointB);
        }
    }
    //print(longestSideLength);
    var dx = longestSideArray[1].y - longestSideArray[0].y;
    var dy = longestSideArray[1].x - longestSideArray[0].x;
    //print(dx);
    //print(dy);
    var deg = degrees(Mathf.Atan(dy/dx));
    var longestSideReadingArray = new Array();
    var longestSideReadingLength = 0f;
    for (var z = 0; z < readingArray.length; z++){
        var pointA2 = readingArray[z];
        var pointB2 = readingArray[(z + 1) % readingArray.length];
        //print("POINT DATA");
        //print("POINT A");
        //print(pointA2.x);
        //print(pointA2.y);
        //print("POINT B");
        //print(pointB2.x);
        //print(pointB2.y);
        //print("----------");
        var rise2 = pointB2.y - pointA2.y;
        var run2 = pointB2.x - pointA2.x;
        var length2 = Mathf.Sqrt(Mathf.Pow(rise2,2) + Mathf.Pow(run2,2));
        if (length2 > longestSideReadingLength){
            /*print("NEW LONGEST LENGTH");
            print(run2);
            print(rise2);
            print("------------------");*/
            longestSideReadingLength = length2;
            longestSideReadingArray = new Array();
            longestSideReadingArray.Add(pointA2);
            longestSideReadingArray.Add(pointB2);
        }
    }
    //print(longestSideReadingLength);
    var dx2 = longestSideReadingArray[1].y - longestSideReadingArray[0].y;
    var dy2 = longestSideReadingArray[1].x - longestSideReadingArray[0].x;
    //print(dx2);
    //print(dy2);
    var deg2 = degrees(Mathf.Atan(dy2/dx2));

    var degDifference = deg - deg2;
    //print(degDifference);
    return degDifference;
}

function calculatePositionFromRelative(arrayOfBasePoints, readingArray, facingAngle){
    var longestSideArray = new Array();
    var longestSideLength = 0f;
    for (var i = 0; i < arrayOfBasePoints.length; i++){
        var pointA = arrayOfBasePoints[i];
        var pointB = arrayOfBasePoints[(i + 1) % arrayOfBasePoints.length];
        var rise = pointB.y - pointA.y;
        var run = pointB.x - pointA.x;
        var length = Mathf.Sqrt(Mathf.Pow(rise,2) + Mathf.Pow(run,2));
        if (length > longestSideLength){
            longestSideLength = length;
            longestSideArray = new Array();
            longestSideArray.Add(pointA);
            longestSideArray.Add(pointB);
        }
    }
    var longestSideReadingArray = new Array();
    var longestSideReadingLength = 0f;
    for (var z = 0; z < readingArray.length; z++){
        var pointA2 = readingArray[z];
        var pointB2 = readingArray[(z + 1) % readingArray.length];
        var rise2 = pointB2.y - pointA2.y;
        var run2 = pointB2.x - pointA2.x;
        var length2 = Mathf.Sqrt(Mathf.Pow(rise2,2) + Mathf.Pow(run2,2));
        if (length2 > longestSideReadingLength){
            longestSideReadingLength = length2;
            longestSideReadingArray = new Array();
            longestSideReadingArray.Add(pointA2);
            longestSideReadingArray.Add(pointB2);
        }
    }
    /*var dx = (longestSideArray[0].x - longestSideReadingArray[0].x);
    var dy = (longestSideArray[0].y - longestSideReadingArray[0].y);
    var lengthCalc = Mathf.Sqrt(Mathf.Pow(dy,2) + Mathf.Pow(dx,2));
    var grad = Mathf.Atan(dy / dx) + radians(facingAngle);
    //var gradiant = () - grad;
    //var legitAngle = Mathf.Atan(grad);
    var risey = Mathf.Cos(grad) * lengthCalc;
    var runx = Mathf.Sin(grad) * lengthCalc;
    //print("-------");
    //print(dx);
    //print(dy);
    var dx2 = (longestSideArray[0].x - runx);
    var dy2 = (longestSideArray[0].y - risey);
    //print("-------");
    //print(degrees(Mathf.Atan(dy / dx)));
    //print(facingAngle);
    print(degrees(Mathf.Atan(dy / dx)));
    print(facingAngle);
    print(facingAngle + degrees(Mathf.Atan(dy / dx)));
    print("_____________");
    //print(degrees(legitAngle));
    //print(facingAngle);
    //print(grad);*/
    var dx = longestSideReadingArray[0].x;
    var dy = longestSideReadingArray[0].y;
    var angle = Mathf.Atan(dy/dx) - radians(facingAngle);
    if (angle < 0){
        angle += Mathf.PI;
    }
    var dist = Mathf.Sqrt(Mathf.Pow(dy,2) + Mathf.Pow(dx,2));
    var xReal = dist * Mathf.Cos(angle);
    var yReal = dist * Mathf.Sin(angle);
    var dx2 = xReal + longestSideArray[0].x;
    var dy2 = yReal + longestSideArray[0].y;
    print(dx2);
    print(dy2);
    //print(degrees(angle));
    print("------");
    var robotLocation = new point(dx2,dy2);
    return robotLocation;
}

function robotDecide(arrayOfLidar){
    
    //var svgString = '<svg width="300" height="300">';

    debugRealLocation.GetComponent.<UI.Text>().text = "Real Location X:" + transform.position.x + " , Y:" + transform.position.z;

    var thisTimeCornerArray = new Array();

    var lastValue = arrayOfLidar[359];
    var lastGrad = arrayOfLidar[358] - arrayOfLidar[359];
    for(var i = 0; i <= arrayOfLidar.length; i++){
        var currentValue = arrayOfLidar[i % arrayOfLidar.length];
        var newGrad = lastValue - currentValue;
        //print(newGrad);
        //<circle cx="10" cy="10" r="2" fill="red"/>

        //var x = currentValue * sind(i);
        //var y = currentValue * cosd(i);
        //svgString += '<circle cx="'+x*10+'" cy="'+y*10+'" r="1" fill="red"/>';

        if (lastGrad < 0 && newGrad > 0 && (Mathf.Abs(lastGrad) - Mathf.Abs(newGrad)) < 0.10){
            //print("corner");
            var x = currentValue * sind(i);
            var y = currentValue * cosd(i);

            var hitpoint = new point(/*RobotLocation.x +*/ x, /*RobotLocation.y +*/ y);
            //print(pointIsInArray(hitpoint));
            if (pointIsInArray(hitpoint) >= 0){
                //print("Point previously encountered, id: " + pointIsInArray(hitpoint));
                Debug.DrawRay (transform.position, returnVector3Angle(i - 1), Color.red, 1, false);
            }else{
                //print("New point found");

                //figure out if it is *acutally* a new point, or just evidence that the robot has moved
                //do this by: seeing if the robot has actually moved from it's last distances, and (possibly) batching corners that can be seen at the same time into categories, then looping through each category to check if it's possible.
                //Ways of KNOWING two shapes are the same - Same distances between corners (check distances between real corners and batched corners), same angles between corners (check angles between real corners and batched corners)


                Debug.DrawRay (transform.position, returnVector3Angle(i - 1), Color.yellow, 1, false);
                //arrayOfPoints.Add(hitpoint);
            }

            thisTimeCornerArray.Add(hitpoint);

            var angleToCast = returnVector3Angle(i - 2);
            var hit: RaycastHit;
            if (Physics.Raycast(transform.position, angleToCast, hit, lidarDistance)){
                //hit.point
                Instantiate(sphere, hit.point, Quaternion.identity);
            }
            //print(i);
            
        }
        lastValue = currentValue;
        lastGrad = newGrad;
    }

    var batchID = parseInt(checkIfCornersBatch(thisTimeCornerArray));
    if (batchID >= 0){
        //print("Seen before mate.");
        //print(returnCornerArrayFromPointsIds(batchList.cornerBatches[thisTimeCornerArray.length][batchID]));
        var batchPoints = returnCornerArrayFromPointsIds(batchList.cornerBatches[thisTimeCornerArray.length][batchID].Split(","[0]));
        var angle = calculateAngleFromRelative(batchPoints,thisTimeCornerArray);
        RobotLocation = calculatePositionFromRelative(batchPoints,thisTimeCornerArray, angle);
        debugRobotLocation.GetComponent.<UI.Text>().text = "Robot Location X:" + RobotLocation.x + " , Y:" + RobotLocation.y;
    }else{
        //print("totally new.");
        for (var kl = 0; kl < thisTimeCornerArray.length; kl++){
            var corner = thisTimeCornerArray[kl];
            //corner.x += RobotLocation.x;
            //corner.y += RobotLocation.y;
            arrayOfPoints.Add(corner);
        }
        batchCorners(thisTimeCornerArray);
    }
    //svgString += "</svg>";
    //print(svgString);

}

function lsub(num){
    var number = num % lidarArray.length;
    if (number < 0){
        number = lidarArray.length + number;
    }
    return number;
}

function sind(deg){
    return Mathf.Sin(radians(deg));
}

function cosd(deg){
    return Mathf.Cos(radians(deg));
}

var angleToGoOff = 1;

var zeroThreshold = 0.005;

function approximateEqualsZero(num){
    if (Mathf.Abs(num) < zeroThreshold){
        return true;
    }
    return false;
}

function angleBetweenPoints(prx,pry,x,y,nx,ny){

    var dx1 = prx - x;
    var dy1 = pry - y;
    var dx2 = x - nx;
    var dy2 = y - ny;

    var deg1 = Mathf.Atan(dy1 / dx1) * 180 / Mathf.PI;
    var deg2 = Mathf.Atan(dy2 / dx2) * 180 / Mathf.PI;
    var resultDegree = Mathf.Abs(deg1 - deg2);
    //print(resultDegree);
    //var p12 = Mathf.Sqrt(Mathf.Pow((prx - x),2) + Mathf.Pow((pry - y),2));

    //var p13 = Mathf.Sqrt(Mathf.Pow((prx - nx),2) + Mathf.Pow((pry - ny),2));

    //var p23 = Mathf.Sqrt(Mathf.Pow((x - nx),2) + Mathf.Pow((y - ny),2));

    //var resultDegree = Mathf.Acos(((Mathf.Pow(p12, 2)) + (Mathf.Pow(p13, 2)) - (Mathf.Pow(p23, 2))) / (2 * p12 * p13)) * 180 / Mathf.PI;
    return resultDegree;
}


/*function robotDecide(arrayOfLidar){
    
    //var lastValue = arrayOfLidar[359];
    //var lastGrad = arrayOfLidar[358] - arrayOfLidar[359];
    for(var i = 0; i < arrayOfLidar.length; i++){
        var prevValue = arrayOfLidar[lsub(i-angleToGoOff)];
        var currentValue = arrayOfLidar[lsub(i)];
        var nextValue = arrayOfLidar[lsub(i + angleToGoOff)];

        var prx = prevValue * sind(i-angleToGoOff);
        var pry = prevValue * cosd(i-angleToGoOff);

        var x = currentValue * sind(i);
        var y = currentValue * cosd(i);

        var nx = nextValue * sind(i+angleToGoOff);
        var ny = nextValue * cosd(i+angleToGoOff);

        var dx1 = prx - x;
        var dy1 = pry - y;

        var dx2 = x - nx;
        var dy2 = y - ny;

        if ((approximateEqualsZero(dx1) && !approximateEqualsZero(dx2))){
        //if (angleBetweenPoints(prx,pry,x,y,nx,ny) % 180 < 120 && angleBetweenPoints(prx,pry,x,y,nx,ny) % 180 > 60){
            Debug.DrawRay (transform.position, returnVector3Angle(i - 1), Color.yellow, 1, false);
            //print(dx1);
            //print(dx2);
            //print("corner");
            //print();
            //print(prx);
            //print(pry);
            //print(x);
            //print(y);
            //print(nx);
            //print(ny);
            var angleToCast = returnVector3Angle(i);
            var hit: RaycastHit;
            if (Physics.Raycast(transform.position, angleToCast, hit, lidarDistance)){
                //hit.point
                Instantiate(sphere, hit.point, Quaternion.identity);

                //find the closest collision (because that is likely to be the corner)


            }

        }

        /*var currentValue = arrayOfLidar[i % arrayOfLidar.length];
        var newGrad = lastValue - currentValue;
        //print(newGrad);
        if (lastGrad < 0 && newGrad > 0 && (Mathf.Abs(lastGrad) - Mathf.Abs(newGrad)) < 0.10){
            print("corner");
            //print(i);
            Debug.DrawRay (transform.position, returnVector3Angle(i - 1), Color.yellow, 1, false);
            var angleToCast = returnVector3Angle(i - 2);
            var hit: RaycastHit;
            if (Physics.Raycast(transform.position, angleToCast, hit, lidarDistance)){
                //hit.point
                Instantiate(sphere, hit.point, Quaternion.identity);
            }
        }
        lastValue = currentValue;
        lastGrad = newGrad;*
        //i++;
        i += angleToGoOff - 1;
    }
}*/

/*function robotDecide(arrayOfLidar){
    
    var lastValue = arrayOfLidar[359];
    var lastGrad = arrayOfLidar[358] - arrayOfLidar[359];
    for(var i = 0; i < arrayOfLidar.length; i++){
        var prevValue = arrayOfLidar[lsub(i-angleToGoOff)];
        var currentValue = arrayOfLidar[lsub(i)];
        var nextValue = arrayOfLidar[lsub(i + angleToGoOff)];

        /*if ((approximateEqualsZero(dx1) && !approximateEqualsZero(dx2))){
        //if (angleBetweenPoints(prx,pry,x,y,nx,ny) % 180 < 120 && angleBetweenPoints(prx,pry,x,y,nx,ny) % 180 > 60){
            Debug.DrawRay (transform.position, returnVector3Angle(i - 1), Color.yellow, 1, false);
            //print(dx1);
            //print(dx2);
            //print("corner");
            //print();
            //print(prx);
            //print(pry);
            //print(x);
            //print(y);
            //print(nx);
            //print(ny);
            var angleToCast = returnVector3Angle(i);
            var hit: RaycastHit;
            if (Physics.Raycast(transform.position, angleToCast, hit, lidarDistance)){
                //hit.point
                Instantiate(sphere, hit.point, Quaternion.identity);

                //find the closest collision (because that is likely to be the corner)


            }

        }*

        var newGrad = lastValue - currentValue;
        //print(newGrad);
        if (lastGrad < 0 && newGrad > 0 && (Mathf.Abs(lastGrad) - Mathf.Abs(newGrad)) < 0.10){

            for (var z = -5; z <= 5; z++){

                prevValue = arrayOfLidar[lsub(i-angleToGoOff + z)];
                currentValue = arrayOfLidar[lsub(i + z)];
                nextValue = arrayOfLidar[lsub(i + angleToGoOff + z)];

                var prx = prevValue * sind(i-angleToGoOff + z);
                var pry = prevValue * cosd(i-angleToGoOff + z);

                var x = currentValue * sind(i + z);
                var y = currentValue * cosd(i + z);

                var nx = nextValue * sind(i+angleToGoOff + z);
                var ny = nextValue * cosd(i+angleToGoOff + z);

                var dx1 = prx - x;
                var dy1 = pry - y;

                var dx2 = x - nx;
                var dy2 = y - ny;


                if ((approximateEqualsZero(dx1) && !approximateEqualsZero(dx2))){
                    //if (angleBetweenPoints(prx,pry,x,y,nx,ny) % 180 < 120 && angleBetweenPoints(prx,pry,x,y,nx,ny) % 180 > 60){
                    Debug.DrawRay (transform.position, returnVector3Angle(i - 1), Color.yellow, 1, false);
                    //print(dx1);
                    //print(dx2);
                    //print("corner");
                    //print();
                    //print(prx);
                    //print(pry);
                    //print(x);
                    //print(y);
                    //print(nx);
                    //print(ny);
                    var angleToCast = returnVector3Angle(i);
                    var hit: RaycastHit;
                    if (Physics.Raycast(transform.position, angleToCast, hit, lidarDistance)){
                        //hit.point
                        Instantiate(sphere, hit.point, Quaternion.identity);

                        //find the closest collision (because that is likely to be the corner)
                    }
                }


            }

            /*print("corner");
            //print(i);
            Debug.DrawRay (transform.position, returnVector3Angle(i - 1), Color.yellow, 1, false);
            var angleToCast = returnVector3Angle(i - 2);
            var hit: RaycastHit;
            if (Physics.Raycast(transform.position, angleToCast, hit, lidarDistance)){
                //hit.point
                Instantiate(sphere, hit.point, Quaternion.identity);
            }*
        }
        lastValue = currentValue;
        lastGrad = newGrad;
        //i++;
        i += angleToGoOff - 1;
    }
}*/