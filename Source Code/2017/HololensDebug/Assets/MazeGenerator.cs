using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Threading;
using System.Threading.Tasks;

public class MazeGenerator : MonoBehaviour {

    public GameObject wallVert;
    public GameObject wallHor;
    public GameObject cellFloor;

    public GameObject self;

    public GameObject mainCamera;
    public GameObject lightBeam;
    public GameObject lightBeamAngle;

    public float cellWidth = 0.3f;

    public int mazeWidth = 21;
    public int mazeHeight = 21;

    public float selfWidth;
    public float selfHeight;

    public Material Red;
    public Material Blue;
    public Material Green;
    public Material Orange;
    public Material Cyan;

    public Material LowQualRed;
    public Material LowQualBlue;
    public Material LowQualGreen;
    public Material LowQualOrange;
    public Material LowQualCyan;

    public bool highQuality;

    public bool finished = false;

    ThreadManager threadmanager = new ThreadManager(32);

    private List<int> maze = new List<int>();
    private string message = "MAP;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,9,0,9,0,9,0,9,0,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,1,0,1,0,1,9,1,0,1,0,1,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,0,0,0,0,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,9,1,0,1,0,1,0,1,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,1,0,1,2,9,2,1,0,0,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,1,0,1,0,1,0,1,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,9,0,9,0,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0";

    // Use this for initialization
    void Start () {
        //print("MAZEGENERATOR LOADING");
        
	}

    public void beginDraw()
    {
        if (highQuality)
        {

        }
        else
        {
            Red = LowQualRed;
            Blue = LowQualBlue;
            Cyan = LowQualCyan;
            Orange = LowQualOrange;
            Green = LowQualGreen;
        }
        drawMaze();
       // interpretMessage(message);
        //t.Start();

        var bounds = calculateOwnBounds().extents;
        selfWidth = bounds.x;
        selfHeight = bounds.z;
    }

    public void moveLightBeam(int tox, int toy)
    {
        //print("MOVED LIGHT BEAM");
        if (tox >= 0 && toy >= 0)
        {
            var cell = tiles[(mazeHeight - toy - 1) * mazeHeight + (mazeWidth - tox - 1)];
            lightBeam.GetComponent<MeshRenderer>().enabled = true;
            lightBeamAngle.GetComponent<MeshRenderer>().enabled = true;
            lightBeam.transform.position = cell.transform.position + Vector3.up;
        }else
        {
            lightBeam.GetComponent<MeshRenderer>().enabled = false;
            lightBeamAngle.GetComponent<MeshRenderer>().enabled = false;
        }
    }

    public void rotateLightBeam(float toAngle)
    {
		lightBeam.transform.rotation = Quaternion.Euler(0, toAngle + transform.rotation.eulerAngles.y + 90, 0);//(0, toAngle, 0);//rotation.eulerAngles.Set(0,toAngle,0);
    }

    void drawEmptyMaze()
    {
        for (int i = 0; i < mazeWidth * mazeHeight; i++)
        {
            maze.Add(1);
        }
    }

    private List<GameObject> tiles = new List<GameObject>();

    void drawMaze()
    {
        int count = 0;
        bool even = false;

        float negativeX = - (cellWidth * (int)(mazeWidth / 2));
        float negativeZ =  - (cellWidth * (int)(mazeHeight / 2));

        float totalWidth = Mathf.Floor(mazeWidth / 2) * cellWidth;
        //transform.position = new Vector3(cellWidth * (int)(mazeWidth / 2), 0f, cellWidth * (int)(mazeHeight / 2));

        cellFloor.transform.SetParent(this.transform);
        wallVert.transform.SetParent(this.transform);
        wallHor.transform.SetParent(this.transform);

        threadmanager.AddLoopingThread(0, mazeHeight, (i) =>
        {
            even = (i % 2 == 0);

            //WIDTH
            for (int x = 0; x < mazeWidth; x++)
            {
                count++;
                GameObject nextObject;
                bool even2 = (x % 2 == 0);
                if (!even)
                {
                    //Real cells or vertical walls
                    if (!even2)
                    {
                        //Cell
                        GameObject cell = Instantiate(cellFloor);
                        float zPos = (cellWidth / 2) + cellWidth * (i / 2);
                        float xPos = totalWidth-((cellWidth / 2) + cellWidth * (x / 2));
                        cell.transform.position = new Vector3(xPos, 0, zPos);
                        tiles.Add(cell);
                        nextObject = cell;
                    }
                    else
                    {
                        //Vertical wall
                        GameObject vertiWall = Instantiate(wallVert);
                        float xPos = totalWidth - (cellWidth * (x / 2));
                        float zPos = (cellWidth / 2) + (cellWidth * (i / 2));
                        float yPos = (cellWidth / 2);
                        vertiWall.transform.position = new Vector3(xPos, yPos, zPos);
                        tiles.Add(vertiWall);
                        nextObject = vertiWall;
                    }
                }
                else
                {
                    //No real cells (either horizontal walls or nothing)
                    if (!even2)
                    {
                        //horizontal wall
                        GameObject horiWall = Instantiate(wallHor);
                        float zPos = cellWidth * (int)(i / 2);
                        float xPos = totalWidth - ((cellWidth / 2) + cellWidth * (int)(x / 2));
                        float yPos = (cellWidth / 2);
                        horiWall.transform.position = new Vector3(xPos, yPos, zPos);
                        tiles.Add(horiWall);
                        nextObject = horiWall;
                    }
                    else
                    {
                        GameObject nothing = new GameObject();
                        //nothing.transform.position = new Vector3(negativeX, 0, negativeZ);
                        tiles.Add(nothing);
                        nextObject = nothing;
                    }
                }
            }
        }).AddEndCalls(()=> {
            setParents();
            print(totalWidth);
        }).addDescription("Generating " + mazeWidth + "x" + mazeHeight + " maze cells. ");

        /*//HEIGHT
        for (int i = 0; i < mazeHeight; i++)
        {
            even = (i % 2 == 0);

            //WIDTH
            for (int x = 0; x < mazeWidth; x++)
            {
                count++;
                GameObject nextObject;
                bool even2 = (x % 2 == 0);
                if (!even)
                {
                    //Real cells or vertical walls
                    if (!even2)
                    {
                        //Cell
                        GameObject cell = Instantiate(cellFloor);
                        float zPos = (cellWidth / 2) + cellWidth * (i / 2);
                        float xPos = (cellWidth / 2) + cellWidth * (x / 2);
                        cell.transform.position = new Vector3(xPos, 0, zPos);
                        tiles.Add(cell);
                        nextObject = cell;
                    }
                    else
                    {
                        //Vertical wall
                        GameObject vertiWall = Instantiate(wallVert);
                        float xPos = (cellWidth * (x / 2));
                        float zPos = (cellWidth / 2) + (cellWidth * (i / 2));
                        float yPos = (cellWidth / 2);
                        vertiWall.transform.position = new Vector3(xPos, yPos, zPos);
                        tiles.Add(vertiWall);
                        nextObject = vertiWall;
                    }
                }else
                {
                    //No real cells (either horizontal walls or nothing)
                    if (!even2)
                    {
                        //horizontal wall
                        GameObject horiWall = Instantiate(wallHor);
                        float zPos = cellWidth * (int)(i / 2);
                        float xPos = (cellWidth / 2) + cellWidth * (int)(x / 2);
                        float yPos = (cellWidth / 2);
                        horiWall.transform.position = new Vector3(xPos, yPos, zPos);
                        tiles.Add(horiWall);
                        nextObject = horiWall;
                    }
                    else
                    {
                        GameObject nothing = new GameObject();
                        tiles.Add(nothing);
                        nextObject = nothing;
                    }
                }
            }
            //mainCamera.GetComponent<Main>().Update();
        }*/

        //combineMeshes(tiles, self);
        //print(calculateOwnBounds().size.x);
        //setParents();
        
    }

    public ThreadManagerLoop loop;

    void setParents()
    {
        loop = threadmanager.AddLoopingThread(0, tiles.Count, (int i) => {
            if (tiles[i].transform.parent == null)
            {
                tiles[i].transform.SetParent(this.transform);
                print("SETTING PARENT " + i + " OF " + tiles.Count);
                //mainCamera.GetComponent<Main>().Update();
            }
            else
            {
                print("PARENT " + i + " OF " + tiles.Count + " ALREADY SET");
            }
        });
        loop.AddEndCalls(() => {
            finished = true;
            #if UNITY_EDITOR
            interpretMessage(message);
            #endif
            mainCamera.GetComponent<Main>().moveMap();
            print(calculateOwnBounds().extents.x);
        }).addDescription("Resolving object heirachy. ");

        //print(loop.loopTo);
        //print(loop.loopCounter);
        //print(loop.threadID);
    }

    public Bounds calculateOwnBounds()
    {
        // First find a center for your bounds.
        Vector3 center = Vector3.zero;

        foreach (Transform child in this.transform)
        {
            if (child.gameObject.GetComponent<Renderer>() != null)
            {
                center += child.gameObject.GetComponent<Renderer>().bounds.center;
            }
            
        }
        center /= this.transform.childCount; //center is average center of children

        //Now you have a center, calculate the bounds by creating a zero sized 'Bounds', 
        Bounds bounds = new Bounds(center, Vector3.zero);

        foreach (Transform child in this.transform)
        {
            if (child.gameObject.GetComponent<Renderer>() != null)
            {
                bounds.Encapsulate(child.gameObject.GetComponent<Renderer>().bounds);
            }
        }
        return bounds;
    }

    public void interpretMessage(string message)
    {
        if (message.Contains("MAP;"))
        {

            //textBlock.Text += "Started drawing map" + "\n";

            //ex M:0,1,1,0,1,1,1
            print("DRAWING MAZE");

            string newMessage = message.Replace("MAP;", "");
            string[] mapArray = newMessage.Split(","[0]);
            //textBlock.Text += "Map is of size " + mapArray.Length + "\n";

            List<int> mapList = new List<int>();
            //Debug.WriteLine(mapArray);
            for (int x = 0; x < mapArray.Length; x++)
            {
                if (mapArray[x] != "")
                {
                    //Debug.Write(mapArray[0]);
                    //Debug.Write(mapArray.Length);
                    mapList.Add(int.Parse(mapArray[x]));
                }
            }
            print("MAP WAS " + mapList.Count + " LONG");
            mapList.Reverse();
            maze = mapList;
            recolorMaze();

        }

        else if (message.Contains("CMP;"))
        {

            //ex C:256.8

            double compassSS = double.Parse(message.Replace("CMP;", ""));

            //textBlock.Text += "Recieved Accelerometer data" + "\n";

        }

        else if (message.Contains("CRD;"))
        {

            //ex X:22,77

            string[] coords = message.Replace("CRD;", "").Split(","[0]);
            


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
            


        }

        else
        {
            
        }
    }

    //color codes
    //RED: Black tile, heat victim
    //BLUE: Normal wall, normal unexplored tile
    //ORANGE: Ramp
    //GREEN: Silver
    //CYAN: Explored

    //1 is explored
    //2 is black tile (and surrounding wall)
    //3 is silver tile
    //4-6 are temperture
    //7 is ramp
    //9 is wall


    // Update is called once per frame
    void Update () {
        threadmanager.Run();
        //print(threadmanager.returnThreads()[0].progress());
        var threads = threadmanager.returnThreads();
        if (threads.Count > 0) { 
            mainCamera.GetComponent<Main>().UpdateUIMessageText(threads[0].threadDescription() + (int)(threads[0].progress() * 100) + "% done");
        }else
        {
            mainCamera.GetComponent<Main>().UpdateUIMessageText("");
        }
        //print("MAIN THREAD FREE");

    }

	Vector3 returnCoordsOfTileAt(int tilezx, int tilezy){
		var cell = tiles[(mazeHeight - tilezy - 1) * mazeHeight + (mazeWidth - tilezx - 1)];
		print (cell.transform.position.x);
		print (cell.transform.position.y);
		return cell.transform.position;
	}

	public Vector3 returnTileDelta(int tilesx, int tilesy){
		print (tilesx);
		print(tilesy);
		return returnCoordsOfTileAt(tilesx, tilesy) - returnCoordsOfTileAt((int)Mathf.Floor(mazeWidth / 2), (int)Mathf.Floor (mazeHeight / 2));
	}

    void recolorMaze()
    {
        /*for (int i = 0; i < maze.Count; i++)
        {
            if (i >= tiles.Count)
            {
                break;
            }
            GameObject recolorCell = tiles[i];
            if (recolorCell.name != "New Game Object")
            {
                recolorCell.GetComponent<Renderer>().enabled = true;
                var rend = recolorCell.GetComponent<Renderer>();
                //print(maze[i]);
                switch (maze[i])
                {
                    case 0:
                        rend.enabled = false;
                        break;
                    case 1:
                        rend.material = Cyan;
                        break;
                    case 2:
                        rend.material = Red;
                        break;
                    case 3:
                        rend.material = Green;
                        break;
                    case 7:
                        rend.material = Orange;
                        break;
                    case 9:
                        rend.material = Blue;
                        break;
                }
            }
        }*/
        threadmanager.AddLoopingThread(0, maze.Count, (i) =>
        {
            if (i >= tiles.Count)
            {

            } else { 
                GameObject recolorCell = tiles[i];
                if (recolorCell.name != "New Game Object")
                {
                    recolorCell.GetComponent<Renderer>().enabled = true;
                    var rend = recolorCell.GetComponent<Renderer>();
                    //print(maze[i]);
                    switch (maze[i])
                    {
                        case 0:
                            rend.enabled = false;
                            break;
                        case 1:
                            rend.material = Cyan;
                            break;
                        case 2:
                            rend.material = Red;
                            break;
                        case 3:
                            rend.material = Green;
                            break;
                        case 7:
                            rend.material = Orange;
                            break;
                        case 9:
                            rend.material = Blue;
                            break;
                    }
                }
            }
        }).addDescription("Drawing Maze ");
    }

    //void recolorMaze(List<int> maze)
    //{
    //    for (int i = 0; i < maze.Count; i++)
    //    {
    //        if (i >= tiles.Count)
    //        {
    //            break;
    //        }
    //        GameObject recolorCell = tiles[i];
    //        if (recolorCell.name != "New Game Object")
    //        {
    //            recolorCell.GetComponent<Renderer>().enabled = true;
    //            var rend = recolorCell.GetComponent<Renderer>();
    //            switch (maze[i])
    //            {
    //                case 0:
    //                    rend.enabled = false;
    //                    break;
    //                case 1:
    //                    rend.enabled = true;
    //                    rend.material = Blue;
    //                    break;
    //                case 2:
    //                    rend.enabled = true;
    //                    rend.material = Red;
    //                    break;
    //                case 3:
    //                    rend.enabled = true;
    //                    rend.material = Green;
    //                    break;
    //                case 7:
    //                    rend.enabled = true;
    //                    rend.material = Orange;
    //                    break;
    //                case 9:
    //                    rend.enabled = true;
    //                    rend.material = Blue;
    //                    break;
    //            }
    //        }
    //    }
    //}

    void combineMeshes(List<GameObject> obj, GameObject parent)
    {
        Vector3 position = parent.transform.position;
        parent.transform.position = Vector3.zero;

        MeshFilter[] meshFilters = new MeshFilter[obj.Count];
        var x = 0;
        foreach (var element in obj)
        {
            meshFilters[x] = element.GetComponent<MeshFilter>();
            x++;
        }
        CombineInstance[] combine = new CombineInstance[meshFilters.Length];
        int i = 0;
        while (i < meshFilters.Length)
        {
            combine[i].mesh = meshFilters[i].sharedMesh;
            combine[i].transform = meshFilters[i].transform.localToWorldMatrix;
            Destroy(meshFilters[i].gameObject);
            i++;
        }
        parent.transform.GetComponent<MeshFilter>().mesh = new Mesh();
        parent.transform.GetComponent<MeshFilter>().mesh.CombineMeshes(combine, true, true);
        parent.transform.gameObject.SetActive(true);

        parent.transform.position = position;

        parent.AddComponent<MeshCollider>();

    }
}
