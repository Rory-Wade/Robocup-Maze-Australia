using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using Windows.Devices.Bluetooth;
using Windows.Devices.Bluetooth.Rfcomm;
using Windows.Networking.Sockets;
using Windows.Storage.Streams;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Input;
using Windows.UI.Xaml.Media;
using Windows.UI.Xaml.Navigation;
using Windows.UI.Xaml.Shapes;

// The Blank Page item template is documented at http://go.microsoft.com/fwlink/?LinkId=402352&clcid=0x409

namespace Bluetooth
{
    /// <summary>
    /// An empty page that can be used on its own or navigated to within a Frame.
    /// </summary>
    public sealed partial class MainPage : Page
    {

        //public Timer timer;

        private System.DateTime time;

        public MainPage()
        {
            this.InitializeComponent();
            time = System.DateTime.Now;
            //timer2 = new Timer()
            Init();
            ReplayUI.Visibility = Visibility.Collapsed;
        }

        void Init()
        {
            InitializeRfcommServer();
            progressIndicator.IsActive = true;

            //timer = new Timer(TimerAction, null, (int)TimeSpan.FromMilliseconds(1).TotalMilliseconds, Timeout.Infinite);
        }

        private StreamSocket socket;
        private DataWriter writer;
        private RfcommServiceProvider rfcommProvider;
        private StreamSocketListener socketListener;

        private bool replaying = false;

        private List<Tuple<int, string>> dataRecording = new List<Tuple<int, string>>();

        private bool competitionMode = false;

        private int mapWidth = 75;
        private int mapHeight = 75;

        private int maxTemperture = 50;
        private int minTemperture = 10;

        private int robotX = 0;
        private int robotY = 0;

        private int silverX = 0;
        private int silverY = 0;

        private double canvasWidth;
        private double canvasHeight;

        public const byte SdpServiceNameAttributeType = (4 << 3) | 5;
        public const string SdpServiceName = "Australia Robocup";
        public static readonly Guid RfcommChatServiceUuid = Guid.Parse("34B1CF4D-1069-4AD6-89B6-E161D79BE4D8");
        public const UInt16 SdpServiceNameAttributeId = 0x100;

        /*private void TimerAction(object state)
        {
            Debug.WriteLine("TIMER +++++");
            milliseconds++;
        }*/

        private string GenerateReplayFileString()
        {
            string replayString = "";
            for (int i = 0; i < dataRecording.Count; i++)
            {
                replayString += dataRecording[i].Item1.ToString() + "`" + dataRecording[i].Item2 + "\n";
            }
            return replayString;
        }

        private async void SaveFile()
        {
            var savePicker = new Windows.Storage.Pickers.FileSavePicker();
            savePicker.SuggestedStartLocation =
                Windows.Storage.Pickers.PickerLocationId.DocumentsLibrary;
            // Dropdown of file types the user can save the file as
            savePicker.FileTypeChoices.Add("Robot Replay File", new List<string>() { ".rep" });
            // Default file name if the user does not type one in or select a file to replace
            savePicker.SuggestedFileName = "Replay " + System.DateTime.Now.ToString();

            Windows.Storage.StorageFile file = await savePicker.PickSaveFileAsync();
            if (file != null)
            {
                // Prevent updates to the remote version of the file until
                // we finish making changes and call CompleteUpdatesAsync.
                Windows.Storage.CachedFileManager.DeferUpdates(file);
                // write to file
                await Windows.Storage.FileIO.WriteTextAsync(file, GenerateReplayFileString());
                // Let Windows know that we're finished changing the file so
                // the other app can update the remote version of the file.
                // Completing updates may require Windows to ask for user input.
                Windows.Storage.Provider.FileUpdateStatus status =
                    await Windows.Storage.CachedFileManager.CompleteUpdatesAsync(file);
                if (status == Windows.Storage.Provider.FileUpdateStatus.Complete)
                {
                    this.textBlock.Text = "Replay " + file.Name + " was saved.";
                }
                else
                {
                    this.textBlock.Text = "Replay " + file.Name + " couldn't be saved.";
                }
            }
            else
            {
                this.textBlock.Text = "Operation cancelled.";
            }

        }

        private async void InitializeRfcommServer()
        {

            try
            {
                rfcommProvider = await RfcommServiceProvider.CreateAsync(RfcommServiceId.FromUuid(RfcommChatServiceUuid));
            }
            // Catch exception HRESULT_FROM_WIN32(ERROR_DEVICE_NOT_AVAILABLE).
            catch (Exception ex) when ((uint)ex.HResult == 0x800710DF)
            {
                // The Bluetooth radio may be off.
                return;
            }


            // Create a listener for this service and start listening
            socketListener = new StreamSocketListener();
            socketListener.ConnectionReceived += OnConnectionReceived;
            var rfcomm = rfcommProvider.ServiceId.AsString();

            await socketListener.BindServiceNameAsync(rfcommProvider.ServiceId.AsString(),
                SocketProtectionLevel.BluetoothEncryptionAllowNullAuthentication);

            //Debug.WriteLine(socketListener.Information);
            Debug.WriteLine(rfcomm);
            // Set the SDP attributes and start Bluetooth advertising
            InitializeServiceSdpAttributes(rfcommProvider);

            try
            {
                rfcommProvider.StartAdvertising(socketListener, true);
            }
            catch (Exception e)
            {
                Debug.WriteLine(e);
                // If you aren't able to get a reference to an RfcommServiceProvider, tell the user why.  Usually throws an exception if user changed their privacy settings to prevent Sync w/ Devices.  
                return;
            }
        }

        private void InitializeServiceSdpAttributes(RfcommServiceProvider rfcommProvider)
        {
            var sdpWriter = new DataWriter();

            // Write the Service Name Attribute.
            sdpWriter.WriteByte(SdpServiceNameAttributeType);

            // The length of the UTF-8 encoded Service Name SDP Attribute.
            sdpWriter.WriteByte((byte)SdpServiceName.Length);

            // The UTF-8 encoded Service Name value.
            sdpWriter.UnicodeEncoding = Windows.Storage.Streams.UnicodeEncoding.Utf8;
            sdpWriter.WriteString(SdpServiceName);

            // Set the SDP Attribute on the RFCOMM Service Provider.
            rfcommProvider.SdpRawAttributes.Add(SdpServiceNameAttributeId, sdpWriter.DetachBuffer());
        }

        private async void SendMessage(string message)
        {
            // There's no need to send a zero length message
            if (message.Length != 0)
            {
                // Make sure that the connection is still up and there is a message to send
                if (socket != null)
                {
                    writer.WriteUInt32((uint)message.Length);
                    writer.WriteString(message);

                    //Send message

                    await writer.StoreAsync();

                }
                else
                {
                    //rootPage.NotifyUser("No clients connected, please wait for a client to connect before attempting to send a message", NotifyType.StatusMessage);
                }
            }
        }

        private async void Disconnect()
        {
            if (rfcommProvider != null)
            {
                rfcommProvider.StopAdvertising();
                rfcommProvider = null;
            }

            if (socketListener != null)
            {
                socketListener.Dispose();
                socketListener = null;
            }

            if (writer != null)
            {
                writer.DetachStream();
                writer = null;
            }

            if (socket != null)
            {
                socket.Dispose();
                socket = null;
            }
            await Dispatcher.RunAsync(Windows.UI.Core.CoreDispatcherPriority.Normal, () =>
            {
                //Do stuff on disconnection
            });
        }

        private async void OnConnectionReceived(
            StreamSocketListener sender, StreamSocketListenerConnectionReceivedEventArgs args)
        {


            // Don't need the listener anymore
            socketListener.Dispose();
            socketListener = null;

            try
            {
                socket = args.Socket;
            }
            catch (Exception e)
            {
                await Dispatcher.RunAsync(Windows.UI.Core.CoreDispatcherPriority.Normal, () =>
                {
                    //Errored somehow
                    Debug.WriteLine(e);
                });
                Disconnect();
                return;
            }

            // Note - this is the supported way to get a Bluetooth device from a given socket
            var remoteDevice = await BluetoothDevice.FromHostNameAsync(socket.Information.RemoteHostName);

            writer = new DataWriter(socket.OutputStream);
            var reader = new DataReader(socket.InputStream);
            bool remoteDisconnection = false;

            await Dispatcher.RunAsync(Windows.UI.Core.CoreDispatcherPriority.Normal, () =>
            {
                //Connected successfully
                //Debug.WriteLine("Connected");
                progressIndicator.IsActive = false;
                textBlock.Text += "Connected to " + remoteDevice.Name + "\n";
                time = System.DateTime.Now;
            });

            // Infinite read buffer loop
            while (true)
            {
                try
                {
                    // Based on the protocol we've defined, the first uint is the size of the message
                    uint readLength = await reader.LoadAsync(sizeof(uint));

                    // Check if the size of the data is expected (otherwise the remote has already terminated the connection)
                    if (readLength < sizeof(uint))
                    {
                        remoteDisconnection = true;
                        break;
                    }
                    uint currentLength = reader.ReadUInt32();

                    // Load the rest of the message since you already know the length of the data expected.  
                    readLength = await reader.LoadAsync(currentLength);

                    // Check if the size of the data is expected (otherwise the remote has already terminated the connection)
                    if (readLength < currentLength)
                    {
                        remoteDisconnection = true;
                        break;
                    }
                    string message = reader.ReadString(currentLength);
                    dataRecording.Add(new Tuple<int, string>((int)(System.DateTime.Now - time).TotalMilliseconds, message));


                    await Dispatcher.RunAsync(Windows.UI.Core.CoreDispatcherPriority.Normal, () =>
                    {
                        //Message recieved
                        Debug.WriteLine(message);

                        if (!replaying)
                        {
                            interpretMessage(message);
                        }
                        


                    });
                }
                // Catch exception HRESULT_FROM_WIN32(ERROR_OPERATION_ABORTED).
                catch (Exception ex) when ((uint)ex.HResult == 0x800703E3)
                {
                    await Dispatcher.RunAsync(Windows.UI.Core.CoreDispatcherPriority.Normal, () =>
                    {

                    });
                    break;
                }
            }

            reader.DetachStream();
            if (remoteDisconnection)
            {
                Disconnect();
                await Dispatcher.RunAsync(Windows.UI.Core.CoreDispatcherPriority.Normal, () =>
                {

                });
            }
        }

        private void interpretMessage(string message)
        {
            if (message.Contains("MAP;"))
            {

                //textBlock.Text += "Started drawing map" + "\n";

                //ex M:0,1,1,0,1,1,1

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

                UpdateMap(mapList);
                textBlock.Text += "Done drawing map" + "\n";

            }

            else if (message.Contains("CMP;"))
            {

                //ex C:256.8

                double compassSS = double.Parse(message.Replace("CMP;", ""));

                //textBlock.Text += "Recieved Accelerometer data" + "\n";

                UpdateCompass((float)compassSS);

            }

            else if (message.Contains("CRD;"))
            {

                //ex X:22,77

                string[] coords = message.Replace("CRD;", "").Split(","[0]);
                robotX = int.Parse(coords[0]);
                robotY = int.Parse(coords[1]);

                textBlock.Text += "Recieved coordinates" + "\n";


            }

            else if (message.Contains("TIL;"))
            {

                //Tile reading
                //ex T;12,2,4,0

                string[] tiles = message.Replace("TIL;", "").Split(","[0]);

                UpdateTiles(int.Parse(tiles[0]), int.Parse(tiles[1]), int.Parse(tiles[2]), int.Parse(tiles[3]));

                textBlock.Text += "Recieved Tile Data" + "\n";

            }

            else if (message.Contains("HEA;"))
            {
                //Temperture
                //leftA,leftS,rightA,rightS

                string[] temps = message.Replace("HEA;", "").Split(","[0]);
                UpdateTempertures(int.Parse(temps[0]), int.Parse(temps[1]), int.Parse(temps[2]), int.Parse(temps[3]));

            }
            else if (message.Contains("CPU;"))
            {

                float cpuUsage = float.Parse(message.Replace("CPU;", ""));
                CPUPercentage.Text = ((int)cpuUsage).ToString() + "%";
                CPUUtilization.Value = cpuUsage;

                if (cpuUsage < 50)
                {
                    CPUUtilization.Foreground = new SolidColorBrush(Windows.UI.Colors.Lime);
                }
                else if (cpuUsage < 75)
                {
                    CPUUtilization.Foreground = new SolidColorBrush(Windows.UI.Colors.Yellow);
                }
                else if (cpuUsage < 90)
                {
                    CPUUtilization.Foreground = new SolidColorBrush(Windows.UI.Colors.Orange);
                }
                else
                {
                    CPUUtilization.Foreground = new SolidColorBrush(Windows.UI.Colors.Red);
                }

            }


            else if (message.Contains("MEM;"))
            {

                float memUsage = float.Parse(message.Replace("MEM;", ""));
                RAMPercentage.Text = ((int)memUsage).ToString() + "%";
                RAMUtilization.Value = memUsage;

                if (memUsage < 50)
                {
                    RAMUtilization.Foreground = new SolidColorBrush(Windows.UI.Colors.Lime);
                }
                else if (memUsage < 75)
                {
                    RAMUtilization.Foreground = new SolidColorBrush(Windows.UI.Colors.Yellow);
                }
                else if (memUsage < 90)
                {
                    RAMUtilization.Foreground = new SolidColorBrush(Windows.UI.Colors.Orange);
                }
                else
                {
                    RAMUtilization.Foreground = new SolidColorBrush(Windows.UI.Colors.Red);
                }

            }
            else if (message.Contains("LST;"))
            {

                string[] lst = message.Replace("LST;", "").Split(","[0]);
                silverX = int.Parse(lst[0]);
                silverY = int.Parse(lst[1]);


            }

            else
            {
                textBlock.Text += message + "\n";
            }
        }

        private void SendButton_Click(object sender, RoutedEventArgs e)
        {
            SendMessage(textBox.Text);
            textBlock.Text += ">" + textBox.Text + "\n";
            //CompassAngle += 1;
            //UpdateCompass(CompassAngle);

        }

        void UpdateTiles(int up, int right, int down, int left)
        {
            TilesUp.Text = (up / 300).ToString();
            TilesRight.Text = (right / 300).ToString();
            TilesDown.Text = (down / 300).ToString();
            TilesLeft.Text = (left / 300).ToString();
        }

        void UpdateTempertures(int leftAmbient, int leftSpot, int rightAmbient, int rightSpot)
        {
            LeftAmbient.Text = leftAmbient.ToString() + "°";
            RightAmbient.Text = rightAmbient.ToString() + "°";

            RightSpot.Text = rightSpot.ToString() + "°";
            LeftSpot.Text = leftSpot.ToString() + "°";

            RightTempMax.Text = maxTemperture.ToString() + "°";
            RightTempMin.Text = minTemperture.ToString() + "°";

            LeftTempMax.Text = maxTemperture.ToString() + "°";
            LeftTempMin.Text = minTemperture.ToString() + "°";

            AmbientLeft.Value = ProgressBarValue(minTemperture, maxTemperture, leftAmbient);
            AmbientRight.Value = ProgressBarValue(minTemperture, maxTemperture, rightAmbient);
            TempertureLeft.Value = ProgressBarValue(minTemperture, maxTemperture, leftAmbient);
            TempertureRight.Value = ProgressBarValue(minTemperture, maxTemperture, leftAmbient);


        }

        float ProgressBarValue(int min, int max, int current)
        {

            float minFloat = min;
            float maxFloat = max;
            float currentFloat = current;

            float progress = (currentFloat - minFloat) / (maxFloat - minFloat);

            return progress;
        }

        private void UpdateCompass(float angle)
        {
            Compass.RenderTransform = new CompositeTransform { Rotation = angle, CenterX = 50, CenterY = 50 };
            CompassBearing.Text = angle.ToString() + "°";
        }

        List<Rectangle> mapList = new List<Rectangle>();

        private void UpdateMap(List<int> newList) {
            for (int i = 0; i < newList.Count; i++)
            {
                //so, 0 is nothing, (no color)
                //1 is explored, (blue)
                //2 is black tile (and surrounding wall), (black)
                //3 is silver tile, (grey)
                //4-6 are temperture
                //7 is ramp, (orangered)
                //9 is wall, (creame)

                int currentThing = newList[i];

                SolidColorBrush newColor = new SolidColorBrush(Windows.UI.Colors.Transparent);

                if (currentThing == 0)
                {
                    newColor = new SolidColorBrush(Windows.UI.Colors.Transparent);
                }

                if (currentThing == 1)
                {
                    newColor = new SolidColorBrush(Windows.UI.Colors.SkyBlue);
                }

                if (currentThing == 2)
                {
                    newColor = new SolidColorBrush(Windows.UI.Colors.Black);
                }

                if (currentThing == 3)
                {
                    newColor = new SolidColorBrush(Windows.UI.Colors.Silver);
                }

                if (currentThing == 3)
                {
                    newColor = new SolidColorBrush(Windows.UI.Colors.OrangeRed);
                }

                if (currentThing == 8)
                {
                    newColor = new SolidColorBrush(Windows.UI.Colors.Red);
                }

                if (currentThing == 9)
                {
                    newColor = new SolidColorBrush(Windows.UI.Colors.Black);
                }

                if ((int)i / mapHeight == silverY && i % mapWidth == silverX)
                {
                    newColor = new SolidColorBrush(Windows.UI.Colors.Green);
                }

                if ((int)i / mapHeight == robotY && i % mapWidth == robotX)
                {
                    newColor = new SolidColorBrush(Windows.UI.Colors.Yellow);
                }

                if (i < mapList.Count)
                {
                    mapList[i].Fill = newColor;
                }


            }
        }

        private void TextBlock_Tapped(object sender, TappedRoutedEventArgs e)
        {

            if (competitionMode)
            {
                ((TextBlock)sender).Text = "Debug Mode";
                ((TextBlock)sender).Foreground = new SolidColorBrush(Windows.UI.Colors.Black);
            }
            else
            {
                ((TextBlock)sender).Text = "Competition Mode";
                ((TextBlock)sender).Foreground = new SolidColorBrush(Windows.UI.Colors.Red);
            }

            competitionMode = !(competitionMode);
        }

        double maxCellWidth = 0.83333333333333;

        private void MakeMap(int width, int height)
        {
            double baseWidth = (ShapeCanvas.Width / width) * 2;
            double baseHeight = (ShapeCanvas.Height / height) * 2;

            double wallWidth = 1 - maxCellWidth;

            double yPos = 0.0;
            for (int i = 0; i < height; i++)
            {
                //mapDisplayArray.Add(new List<Rectangle>());
                if (i % 2 != 0)
                {
                    yPos += baseHeight * wallWidth;
                }
                else if (i != 0)
                {
                    yPos += baseHeight * maxCellWidth;
                }
                double xPos = 0;
                for (int x = 0; x < width; x++)
                {
                    bool odd = i % 2 == 0;
                    bool oddTwo = x % 2 == 0;

                    double cellheight = 0.0;
                    double cellWidth = 0.0;
                    if (odd)
                    {
                        cellheight = baseHeight * wallWidth;
                    }
                    else
                    {
                        cellheight = baseHeight * maxCellWidth;
                    }

                    if (oddTwo)
                    {
                        cellWidth = baseWidth * wallWidth;
                    }
                    else
                    {
                        cellWidth = baseWidth * maxCellWidth;
                    }

                    var cell = new Rectangle()
                    {
                        Width = cellWidth,
                        Height = cellheight,


                        Stroke = new SolidColorBrush(Windows.UI.Colors.LightGray),
                        StrokeThickness = 0.2,
                        //cell.Fill = new SolidColorBrush(Windows.UI.Colors.Black);

                        Margin = new Thickness(left: xPos, top: yPos, right: 0, bottom: 0)
                    };
                    ShapeCanvas.Children.Add(cell);

                    xPos += cellWidth;
                    mapList.Add(cell);
                    //mapDisplayArray[mapDisplayArray.Count - 1].Add(cell);
                }
            }
        }

        private void Grid_Loaded(object sender, RoutedEventArgs e)
        {
            MakeMap(mapWidth, mapHeight);
            canvasHeight = ShapeCanvas.Height;
            canvasWidth = ShapeCanvas.Width;
        }

        private void Button_Click_1(object sender, RoutedEventArgs e)
        {
            if (!replaying)
            {
                Disconnect();
                Init();
                textBlock.Text += "Dropped connection. Opening for reconnection." + "\n";
            }
            else
            {
                replaying = false;
                textBlock.Text += "Quit Replay Mode" + "\n";
                Title.Text = "Debug Mode";
                Title.Foreground = new SolidColorBrush(Windows.UI.Colors.Black);
                ReplayUI.Visibility = Visibility.Collapsed;
                RelogButton.Content = "Reconnect";
            }
            
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            SendMessage("C:P");
        }

        private void Button_ZoomIn(object sender, RoutedEventArgs e)
        {
            ShapeCanvas.RenderTransform = new CompositeTransform { ScaleX = 4, ScaleY = 4 };
            ShapeCanvas.Height = canvasHeight * 4;
            ShapeCanvas.Width = canvasWidth * 4;
            //SaveFile();
        }

        private void Button_ZoomOut(object sender, RoutedEventArgs e)
        {
            ShapeCanvas.RenderTransform = new CompositeTransform { ScaleX = 1, ScaleY = 1 };
            ShapeCanvas.Height = canvasHeight;
            ShapeCanvas.Width = canvasWidth;
        }

        private void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            SaveFile();
        }

        private void RestartButton_Click(object sender, RoutedEventArgs e)
        {
            textBlock.Text = "";
            silverX = 0;
            silverY = 0;
            time = System.DateTime.Now;
            dataRecording = new List<Tuple<int, string>>();
        }

        private async void LoadButton_Click(object sender, RoutedEventArgs e)
        {
            var picker = new Windows.Storage.Pickers.FileOpenPicker();
            picker.ViewMode = Windows.Storage.Pickers.PickerViewMode.List;
            picker.SuggestedStartLocation = Windows.Storage.Pickers.PickerLocationId.DocumentsLibrary;
            picker.FileTypeFilter.Add(".rep");

            Windows.Storage.StorageFile file = await picker.PickSingleFileAsync();
            if (file != null)
            {
                // Application now has read/write access to the picked file
                this.textBlock.Text = "Picked replay: " + file.Name;
                //IInputStream openfile = (await file.OpenSequentialReadAsync());
                string text = await Windows.Storage.FileIO.ReadTextAsync(file);
                //Debug.Write(text);
                string[] textSplit = text.Split(new[] { "\n" }, StringSplitOptions.None);
                FormReplayArray(textSplit);
            }
            else
            {
                this.textBlock.Text = "Operation cancelled.";
            }
        }

        private void FormReplayArray(string[] fromStrings)
        {
            for (int i = 0; i < fromStrings.Length; i++)
            {
                string[] currentLine = fromStrings[i].Split("`"[0]);
                if (currentLine.Length == 2)
                {
                    int time = int.Parse(currentLine[0]);
                    string data = currentLine[1];

                    dataRecording.Add(new Tuple<int, string>(time, data));

                }
            }

            textBlock.Text += "\nReplay loaded.\n";
            replaying = true;

            Title.Text = "Replay Mode";
            Title.Foreground = new SolidColorBrush(Windows.UI.Colors.Black);

            ReplayUI.Visibility = Visibility.Visible;
            RelogButton.Content = "End Replay";

            progressIndicator.Visibility = Visibility.Collapsed;

        }

        private int replayIndex = 0;

        private void StepButton(object sender, RoutedEventArgs e)
        {

            if (replayIndex < dataRecording.Count)
            {
                playingReplay = false;
                ReplayPlayButton.Content = "Play";
                interpretMessage(dataRecording[replayIndex].Item2);
                replayIndex++;
                var appView = Windows.UI.ViewManagement.ApplicationView.GetForCurrentView();
                appView.Title = "Replay Mode - " + replayIndex + " of " + dataRecording.Count;
            }

        }

        private bool playingReplay = false;
        private double[] replaySpeeds = new double[] {0.5, 1, 2, 4, 8, 16, 32};
        private double playSpeed = 1.0;

        private void PlayPauseButton(object sender, RoutedEventArgs e)
        {
            if (!playingReplay)
            {

                ReplayPlayButton.Content = "Pause";
                playingReplay = true;

                playSpeed = replaySpeeds[ReplaySpeed.SelectedIndex];

                Play();
            }
            else
            {
                playingReplay = false;
                ReplayPlayButton.Content = "Play";
            }
            
        }

        private async void Play()
        {
            if (replayIndex < dataRecording.Count && playingReplay)
            {
                TimeSpan ts;
                int time = 0;
                if (replayIndex > 0)
                {
                    time = dataRecording[replayIndex].Item1 - dataRecording[replayIndex - 1].Item1;
                }
                else
                {
                    time = dataRecording[replayIndex].Item1;  
                }

                time = (int)((double)time / playSpeed);

                if (time == 0)
                {
                    time = 1;
                }

                ts = new TimeSpan(0, 0, 0, 0, time);

                //loading.IsActive = true;
                await Task.Delay(ts);
                //loading.IsActive = false;
                interpretMessage(dataRecording[replayIndex].Item2);
                replayIndex++;

                var appView = Windows.UI.ViewManagement.ApplicationView.GetForCurrentView();
                appView.Title = "Replay Mode - " + replayIndex + " of " + dataRecording.Count;

                Play();
            }
            else if (replayIndex >= dataRecording.Count)
            {
                var appView = Windows.UI.ViewManagement.ApplicationView.GetForCurrentView();
                appView.Title = "Replay Mode - Completed replay";
                playingReplay = false;
            }
            

            
            /*
            Task.Delay(ts).ContinueWith(async (x) =>
            {

                replayIndex++;
                Play();
                await Dispatcher.RunAsync(Windows.UI.Core.CoreDispatcherPriority.High, () =>
                {
                    //UI code here
                    interpretMessage(dataRecording[replayIndex].Item2);
                });
            });*/
        }

        private void StepBackButton(object sender, RoutedEventArgs e)
        {
            if (replayIndex > 0)
            {
                playingReplay = false;
                ReplayPlayButton.Content = "Play";
                replayIndex--;
                interpretMessage(dataRecording[replayIndex].Item2);
                var appView = Windows.UI.ViewManagement.ApplicationView.GetForCurrentView();
                appView.Title = "Replay Mode - " + replayIndex + " of " + dataRecording.Count;
            }
        }
    }
}
