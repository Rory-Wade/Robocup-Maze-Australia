using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class UIController : MonoBehaviour {

    public GameObject topLeftText;
    public GameObject centerText;
    public GameObject bottomRightText;

	// Use this for initialization
	void Start () {
        print("UI LOADED");
        //SetInfoText("");
        //SetStatusText("");
        //SetMessageText("");
	}
	
	// Update is called once per frame
	void Update () {
        
	}

    public void SetStatusText(string status)
    {
        topLeftText.GetComponent<TextMesh>().text = status;
    }

    public void SetMessageText(string message)
    {
        centerText.GetComponent<TextMesh>().text = message;
    }

    public void SetInfoText(string info)
    {
        bottomRightText.GetComponent<TextMesh>().text = info;
    }
}
