using System.Collections;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;
using UnityEngine.VR.WSA.Input;
using System.IO;
using System;

public class Main : MonoBehaviour {

    public bool skipSetup = false;
    public GameObject UIController;
    public GameObject MazeRenderer;
    public GameObject GuidingCube;
    public GameObject secondLevel;


    private string messageRecieved;
    #if !UNITY_EDITOR
    private wifiSocket socket;
    #endif
    public bool socketConnected;

    public int mazeWidth = 23;
    public int mazeHeight = 23;
    public float cellWidth = 0.3f;

    public int robotX = 37;
    public int robotY = 39;

    // Use this for initialization
    void Start() {
        //UpdateUIMessageText("Look at the back of the robot\n and press the clicker to callibrate.");
        print("CAMERA LOADED");

        recognizer = new GestureRecognizer();

        recognizer.TappedEvent += Recognizer_TappedEvent;

        recognizer.StartCapturingGestures();

        MazeRenderer.GetComponent<MazeGenerator>().beginDraw();

        #if !UNITY_EDITOR
        socket = new wifiSocket((string recieved) => {
            messageRecieved = recieved;
        });

        socket.load();
#endif

        UpdateUIStatusText("Connecting to computer...");

    }

    private bool mapMoved = false;
    private bool secondMapMoved = false;

    public void moveMap()
    {
        // to put the map at 0,0, it must be set to -(width / 2),0,-(height / 2)
        #if UNITY_EDITOR
        movingPlacementCube = false;
		if (mapMoved){
		placeSecondMap();
		}

        #endif
        if (movingPlacementCube == false && secondMapMoved == false && mapMoved == false)
        {
            secondLevel = Instantiate(MazeRenderer);
            print("PLACING MAP IN CORRECT POSITION");
            Bounds bounds = MazeRenderer.GetComponent<MazeGenerator>().calculateOwnBounds();
            //MazeRenderer.transform.RotateAround(new Vector3(-555.555f, 0, -555.555f), Vector3.up,90/*GuidingCube.transform.rotation.eulerAngles.y*/);// = GuidingCube.transform.rotation;
            float x = -(bounds.extents.x - GuidingCube.transform.position.x);
            float z = -(bounds.extents.z - GuidingCube.transform.position.z);
            print("X:" + x + ", Z:" + z);
            print("Y ROTATION: " + degrees(MazeRenderer.transform.rotation.eulerAngles.y));
            float y = GuidingCube.transform.position.y;
            MazeRenderer.transform.position = new Vector3(x, y, z);
            MazeRenderer.transform.RotateAround(new Vector3(GuidingCube.transform.position.x, 0, GuidingCube.transform.position.z), Vector3.up, GuidingCube.transform.rotation.eulerAngles.y);
            secondLevel.GetComponent<MazeGenerator>().beginDraw();
            mapMoved = true;
        }

    }

    public void placeSecondMap()
    {
        #if UNITY_EDITOR
                movingPlacementCube = false;
        #endif
            print("PLACING MAP IN CORRECT POSITION");
            Bounds bounds = secondLevel.GetComponent<MazeGenerator>().calculateOwnBounds();
            //MazeRenderer.transform.RotateAround(new Vector3(-555.555f, 0, -555.555f), Vector3.up,90/*GuidingCube.transform.rotation.eulerAngles.y*/);// = GuidingCube.transform.rotation;
            float x = -(bounds.extents.x - GuidingCube.transform.position.x);
            float z = -(bounds.extents.z - GuidingCube.transform.position.z);
            print("X:" + x + ", Z:" + z);
            print("Y ROTATION: " + degrees(secondLevel.transform.rotation.eulerAngles.y));
            float y = GuidingCube.transform.position.y;
            secondLevel.transform.position = new Vector3(x/* - ((- Mathf.Floor(mazeWidth / 2) + robotX) * cellWidth)*/, y, z/* - ((- Mathf.Floor(mazeWidth / 2) + robotY) * cellWidth)*/);
			secondLevel.transform.position -= MazeRenderer.GetComponent<MazeGenerator>().returnTileDelta(robotX, robotY);
            secondLevel.transform.RotateAround(new Vector3(GuidingCube.transform.position.x, 0, GuidingCube.transform.position.z), Vector3.up, GuidingCube.transform.rotation.eulerAngles.y);
            secondMapMoved = true;
            secondLevelAdded = true;
    }

    public float radians(float degrees)
    {
        return 0.01745329f * degrees;
    }

    public float degrees(float rad)
    {
        return rad / 0.01745329f;
    }


    // Update is called once per frame
    bool firstUpdate = true;
    bool hudActive = true;
    bool movingPlacementCube = true;
    private int lastRotation;
    public int rotation;
    private int frameCount = 0;
	public void Update () {

        frameCount++;

#if !UNITY_EDITOR
        if (socket.connected == false && frameCount % 300 == 0)
        {
            socket.destroy();
            socket.load();
        }else
        {
            UpdateUIStatusText("");
        }
#endif

#if UNITY_EDITOR
        if (frameCount == 300)
        {
            //secondLevel = Instantiate(MazeRenderer);
            MazeRenderer.GetComponent<MazeGenerator>().moveLightBeam(35,35);
        }
#endif

        if (firstUpdate)
        {
            //MazeRenderer.GetComponent<MazeGenerator>().beginDraw();
            firstUpdate = false;
        }
        if (hudActive)
        {
            MoveHUD();
        }

        if (movingPlacementCube)
        {
            MovePlacementCube();
        }
        
        if (messageRecieved != "")
        {
            interpretMessage(messageRecieved);
            messageRecieved = "";
        }


    }

    bool currentlyLevel0 = true;
    bool secondLevelAdded = false;

    void addSecondLevel()
    {
        movingPlacementCube = true;
    }

    void interpretMessage(string message)
    {
        if (mapMoved)
        {
            if (message.Contains("MAP;"))
            {

                if (currentlyLevel0)
                {
                    MazeRenderer.GetComponent<MazeGenerator>().interpretMessage(message);
                }else if (secondLevelAdded)
                {
                    secondLevel.GetComponent<MazeGenerator>().interpretMessage(message);
                    print("SHOULD HAVE WORKED");
                }else
                {
                    UpdateUIMessageText("Please place a tile where the robot will end up. You will not be allowed to rotate the tile.");
                }

            }

            else if (message.Contains("CMP;"))
            {

                //ex C:256.8

                double compassSS = double.Parse(message.Replace("CMP;", ""));

                if (currentlyLevel0)
                {
                    MazeRenderer.GetComponent<MazeGenerator>().rotateLightBeam((float)compassSS);
                }
                else if (secondLevelAdded)
                {
                    secondLevel.GetComponent<MazeGenerator>().rotateLightBeam((float)compassSS);
                }
                else
                {
                    UpdateUIMessageText("Please place a tile where the robot will end up. You will not be allowed to rotate the tile.");
                }
                //textBlock.Text += "Recieved Accelerometer data" + "\n";

            }

            else if (message.Contains("CRD;"))
            {

                //ex X:22,77

                string[] coords = message.Replace("CRD;", "").Split(","[0]);

				robotX = int.Parse(coords [0]);
				robotY = int.Parse(coords [1]);

                if (currentlyLevel0)
                {
                    secondLevel.GetComponent<MazeGenerator>().moveLightBeam(-1, -1);
                    MazeRenderer.GetComponent<MazeGenerator>().moveLightBeam(int.Parse(coords[0]), int.Parse(coords[1]));
                }
                else if (secondLevelAdded)
                {
                    MazeRenderer.GetComponent<MazeGenerator>().moveLightBeam(-1, -1);
                    secondLevel.GetComponent<MazeGenerator>().moveLightBeam(int.Parse(coords[0]), int.Parse(coords[1]));
                }
                else
                {
                    UpdateUIMessageText("Please place a tile where the robot will end up. You will not be allowed to rotate the tile.");
                }


            }

            else if (message.Contains("TIL;"))
            {

                //Tile reading
                //ex T;12,2,4,0

                string[] tiles = message.Replace("TIL;", "").Split(","[0]);


            }

            else if (message.Contains("HEA;"))
            {
                //Temperture
                //leftA,leftS,rightA,rightS

                string[] temps = message.Replace("HEA;", "").Split(","[0]);


            }
            else if (message.Contains("CPU;"))
            {

                float cpuUsage = float.Parse(message.Replace("CPU;", ""));


            }


            else if (message.Contains("MEM;"))
            {

                float memUsage = float.Parse(message.Replace("MEM;", ""));


            }
            else if (message.Contains("LST;"))
            {

                string[] lst = message.Replace("LST;", "").Split(","[0]);



            }else if (message.Contains("ZLV"))
            {
                if (currentlyLevel0)
                {
                    currentlyLevel0 = false;
                    if (!secondLevelAdded)
                    {
                        addSecondLevel();
                    }
                }else
                {
                    currentlyLevel0 = true;
                }
            }
        }
    }

    void MovePlacementCube()
    {
        if (!mapMoved)
        {
            GuidingCube.transform.position = Vector3.Slerp(GuidingCube.transform.position, (transform.rotation * new Vector3(x: 0, y: 0f, z: 1f)) + transform.position, Time.deltaTime * 2000);
            GuidingCube.transform.rotation = Quaternion.LookRotation(new Vector3(GuidingCube.transform.position.x - this.transform.position.x, 0f, GuidingCube.transform.position.z - this.transform.position.z));
            GuidingCube.transform.position = Vector3.Slerp(GuidingCube.transform.position, (transform.rotation * new Vector3(x: 0, y: -0.1f, z: 1f)) + transform.position, Time.deltaTime * 2000);
        }else
        {
            GuidingCube.transform.position = Vector3.Slerp(GuidingCube.transform.position, (transform.rotation * new Vector3(x: 0, y: 0f, z: 1f)) + transform.position, Time.deltaTime * 2000);
            GuidingCube.transform.position = Vector3.Slerp(GuidingCube.transform.position, (transform.rotation * new Vector3(x: 0, y: -0.1f, z: 1f)) + transform.position, Time.deltaTime * 2000);
        }
    }

    void MoveHUD()
    {
        UIController.transform.position = Vector3.Slerp(UIController.transform.position,(transform.rotation * new Vector3(x:0,y:0,z: 2f)) + transform.position,Time.deltaTime * 20);
        UIController.transform.rotation = Quaternion.LookRotation(UIController.transform.position - this.transform.position);
    }

    public void UpdateUIMessageText(string text)
    {
        UIController.GetComponent<UIController>().SetMessageText(text);
    }

    public void UpdateUIStatusText(string text)
    {
        UIController.GetComponent<UIController>().SetStatusText(text);
    }

    GestureRecognizer recognizer;

    public void Selected()
    {
        print("Selected");
        //MazeRenderer.GetComponent<MazeGenerator>().beginDraw();
    }

    private void Recognizer_TappedEvent(InteractionSourceKind source, int tapCount, Ray headRay)
    {
        // process the event.
        Selected();
        
        if (MazeRenderer.GetComponent<MazeGenerator>().finished)
        {
            if (!mapMoved)
            {
                movingPlacementCube = false;
                moveMap();
            }else
            {
                if (movingPlacementCube)
                {
                    movingPlacementCube = false;
                    placeSecondMap();
                }
            }
        }
    }
}

#if !UNITY_EDITOR
public class wifiSocket
{

    Action<string> messageRecievedAction;
    public bool connected = false;
    Windows.Networking.Sockets.DatagramSocket socket;

    public wifiSocket(Action<string> messageRecieved)
    {
        messageRecievedAction = messageRecieved;
    }

    public void destroy()
    {
        socket.Dispose();
    }

    public async void load()
    {
        socket = new Windows.Networking.Sockets.DatagramSocket();

        socket.MessageReceived += Socket_MessageReceived;

        //You can use any port that is not currently in use already on the machine.
        string serverPort = "1337";

        //Bind the socket to the serverPort so that we can start listening for UDP messages from the UDP echo client.
        await socket.BindServiceNameAsync(serverPort);

        System.Diagnostics.Debug.WriteLine("SOCKET BINDED");
    }

    private async void Socket_MessageReceived(Windows.Networking.Sockets.DatagramSocket sender, Windows.Networking.Sockets.DatagramSocketMessageReceivedEventArgs args)
    {
        //Read the message that was received from the UDP echo client.
        connected = true;

        Stream streamIn = args.GetDataStream().AsStreamForRead();
        StreamReader reader = new StreamReader(streamIn);
        string message = await reader.ReadLineAsync();

        System.Diagnostics.Debug.WriteLine(message);
        messageRecievedAction(message);
    }
}
#endif