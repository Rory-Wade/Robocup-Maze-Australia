using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Diagnostics;
public class ThreadManager {

    public int perUpdate = 0;
    public int updatesThisCall = 0;

    private DateTime runStart;

    public ThreadManager(int miliseconds)
    {
        perUpdate = miliseconds;
    }

    public void Run()
    {
        runStart = DateTime.Now;
        if (threads.Count > 0)
        {
            RunThreads();
        }
        
    }

    public List<ThreadManagerThread> returnThreads()
    {
        return threads;
    }

    /*
     This needs to: have a list of threads,
     run each thread for a time based on its priority,
     interupt each thread, and store each thread's progress
     */
    List<ThreadManagerThread> threads = new List<ThreadManagerThread>();
    
    void RunThreads()
    {
        for (int x = 0; x < threads.Count; x++)
        {
            threads[x].run();
        }
    }

    public int threadWithID(int id)
    {
        for (int i = 0; i < threads.Count; i++)
        {
            if (threads[i].threadID() == id)
            {
                return i;
            }
        }
        return -1;
    }

    public bool UpdateThreader(int threadIdentifier)
    {
        //Return True if the thread can continue
        //False if not
        if ((DateTime.Now - runStart).Milliseconds > (perUpdate / threads.Count) * (threadWithID(threadIdentifier) + 1))
        {
            return false;
        }else
        {
            return true;
        }
    }

    public void PopThread(int threadID)
    {
        for (int i = 0; i < threads.Count; i++)
        {
            if (threads[i].threadID() == threadID)
            {
                threads.RemoveAt(i);
            }
        }
    }

    public int ReturnThreadIDForThread(ThreadManagerThread thread)
    {
        threads.Add(thread);
        return threads.Count - 1;
    }

    public ThreadManagerLoop AddLoopingThread(int loopFrom, int loopTo, Action<int> loopBody)
    {
        return new ThreadManagerLoop(loopfrom: loopFrom, loopto: loopTo, codebody: loopBody, threader: this);
    }

}

public class ThreadManagerThread
{
    ThreadManager parent;
    public virtual float progress() { return 0.0f; }
    public virtual int threadID() { return 0; }
    public virtual string threadDescription() { return ""; }
    public virtual void run()
    {
        
    }
}

public class ThreadManagerLoop : ThreadManagerThread
{
    ThreadManager parent;
    //bool canContinue = false;

    public int loopCounter;
    Action<int> codeBody;
    public int loopTo;
    public int threadIDInternal;
    private float progressCurrent = 0.0f;
    public override float progress() { return progressCurrent; }

    private string internalDescription = "";
    public override string threadDescription()
    {
        return internalDescription;
    }

    public override int threadID()
    {
        return threadIDInternal;
    }

    Action atEnd;

    public ThreadManagerLoop(int loopfrom, int loopto, Action<int> codebody, ThreadManager threader)
    {
        loopCounter = loopfrom;
        loopTo = loopto;
        codeBody = codebody;
        parent = threader;
        threadIDInternal = parent.ReturnThreadIDForThread(this);
    }

    public override void run()
    {
        for (; (loopCounter < loopTo && parent.UpdateThreader(threadIDInternal)); loopCounter++)
        {
            codeBody(loopCounter);
            //UnityAPICompatibilityVersionAttribute.("LOOPING " + i + " OF " + loopTo);
        }
        progressCurrent = (float)loopCounter / (float)loopTo;
        if (progressCurrent == 1)
        {
            if(atEnd != null)
            {
                atEnd();
            }

            parent.PopThread(threadIDInternal);

        }
    }

    public ThreadManagerLoop AddEndCalls(Action closure)
    {
        atEnd = closure;
        return this;
    }

    public ThreadManagerLoop addDescription(string description)
    {
        internalDescription = description;
        return this;
    }

}
