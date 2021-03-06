﻿#pragma checksum "C:\Users\josep\Downloads\Bluetooth\Bluetooth\Bluetooth\MainPage.xaml" "{406ea660-64cf-4c82-b6f0-42d48172a799}" "A8AA968086DDBEB418FD37488E827F76"
//------------------------------------------------------------------------------
// <auto-generated>
//     This code was generated by a tool.
//
//     Changes to this file may cause incorrect behavior and will be lost if
//     the code is regenerated.
// </auto-generated>
//------------------------------------------------------------------------------

namespace Bluetooth
{
    partial class MainPage : 
        global::Windows.UI.Xaml.Controls.Page, 
        global::Windows.UI.Xaml.Markup.IComponentConnector,
        global::Windows.UI.Xaml.Markup.IComponentConnector2
    {
        /// <summary>
        /// Connect()
        /// </summary>
        [global::System.CodeDom.Compiler.GeneratedCodeAttribute("Microsoft.Windows.UI.Xaml.Build.Tasks"," 14.0.0.0")]
        [global::System.Diagnostics.DebuggerNonUserCodeAttribute()]
        public void Connect(int connectionId, object target)
        {
            switch(connectionId)
            {
            case 1:
                {
                    global::Windows.UI.Xaml.Controls.Grid element1 = (global::Windows.UI.Xaml.Controls.Grid)(target);
                    #line 10 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Grid)element1).Loaded += this.Grid_Loaded;
                    #line default
                }
                break;
            case 2:
                {
                    this.SendUI = (global::Windows.UI.Xaml.Controls.Viewbox)(target);
                }
                break;
            case 3:
                {
                    this.progressIndicator = (global::Windows.UI.Xaml.Controls.ProgressRing)(target);
                }
                break;
            case 4:
                {
                    this.Title = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                    #line 35 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.TextBlock)this.Title).Tapped += this.TextBlock_Tapped;
                    #line default
                }
                break;
            case 5:
                {
                    this.RelogButton = (global::Windows.UI.Xaml.Controls.Button)(target);
                    #line 39 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Button)this.RelogButton).Click += this.Button_Click_1;
                    #line default
                }
                break;
            case 6:
                {
                    this.LeftTemperture = (global::Windows.UI.Xaml.Controls.Grid)(target);
                }
                break;
            case 7:
                {
                    this.RightTemperture = (global::Windows.UI.Xaml.Controls.Grid)(target);
                }
                break;
            case 8:
                {
                    global::Windows.UI.Xaml.Controls.Button element8 = (global::Windows.UI.Xaml.Controls.Button)(target);
                    #line 81 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Button)element8).Click += this.Button_Click;
                    #line default
                }
                break;
            case 9:
                {
                    global::Windows.UI.Xaml.Controls.Button element9 = (global::Windows.UI.Xaml.Controls.Button)(target);
                    #line 94 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Button)element9).Click += this.Button_ZoomOut;
                    #line default
                }
                break;
            case 10:
                {
                    global::Windows.UI.Xaml.Controls.Button element10 = (global::Windows.UI.Xaml.Controls.Button)(target);
                    #line 95 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Button)element10).Click += this.Button_ZoomIn;
                    #line default
                }
                break;
            case 11:
                {
                    global::Windows.UI.Xaml.Controls.Button element11 = (global::Windows.UI.Xaml.Controls.Button)(target);
                    #line 96 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Button)element11).Click += this.SaveButton_Click;
                    #line default
                }
                break;
            case 12:
                {
                    global::Windows.UI.Xaml.Controls.Button element12 = (global::Windows.UI.Xaml.Controls.Button)(target);
                    #line 97 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Button)element12).Click += this.RestartButton_Click;
                    #line default
                }
                break;
            case 13:
                {
                    global::Windows.UI.Xaml.Controls.Button element13 = (global::Windows.UI.Xaml.Controls.Button)(target);
                    #line 98 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Button)element13).Click += this.LoadButton_Click;
                    #line default
                }
                break;
            case 14:
                {
                    this.ReplayUI = (global::Windows.UI.Xaml.Controls.Grid)(target);
                }
                break;
            case 15:
                {
                    this.ReplayPlayButton = (global::Windows.UI.Xaml.Controls.Button)(target);
                    #line 100 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Button)this.ReplayPlayButton).Click += this.PlayPauseButton;
                    #line default
                }
                break;
            case 16:
                {
                    global::Windows.UI.Xaml.Controls.Button element16 = (global::Windows.UI.Xaml.Controls.Button)(target);
                    #line 101 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Button)element16).Click += this.StepButton;
                    #line default
                }
                break;
            case 17:
                {
                    global::Windows.UI.Xaml.Controls.Button element17 = (global::Windows.UI.Xaml.Controls.Button)(target);
                    #line 102 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Button)element17).Click += this.StepBackButton;
                    #line default
                }
                break;
            case 18:
                {
                    this.ReplaySpeed = (global::Windows.UI.Xaml.Controls.ComboBox)(target);
                }
                break;
            case 19:
                {
                    this.RAMUtilization = (global::Windows.UI.Xaml.Controls.ProgressBar)(target);
                }
                break;
            case 20:
                {
                    this.RAMPercentage = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 21:
                {
                    this.CPUUtilization = (global::Windows.UI.Xaml.Controls.ProgressBar)(target);
                }
                break;
            case 22:
                {
                    this.CPUPercentage = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 23:
                {
                    this.TempertureRight = (global::Windows.UI.Xaml.Controls.ProgressBar)(target);
                }
                break;
            case 24:
                {
                    this.AmbientRight = (global::Windows.UI.Xaml.Controls.ProgressBar)(target);
                }
                break;
            case 25:
                {
                    this.RightTempMax = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 26:
                {
                    this.RightTempMin = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 27:
                {
                    this.RightSpot = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 28:
                {
                    this.RightAmbient = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 29:
                {
                    this.TempertureLeft = (global::Windows.UI.Xaml.Controls.ProgressBar)(target);
                }
                break;
            case 30:
                {
                    this.AmbientLeft = (global::Windows.UI.Xaml.Controls.ProgressBar)(target);
                }
                break;
            case 31:
                {
                    this.LeftTempMax = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 32:
                {
                    this.LeftTempMin = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 33:
                {
                    this.LeftSpot = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 34:
                {
                    this.LeftAmbient = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 35:
                {
                    this.TilesUp = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 36:
                {
                    this.TilesLeft = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 37:
                {
                    this.TilesDown = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 38:
                {
                    this.TilesRight = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 39:
                {
                    this.ShapeCanvas = (global::Windows.UI.Xaml.Controls.Canvas)(target);
                }
                break;
            case 40:
                {
                    this.Compass = (global::Windows.UI.Xaml.Controls.Image)(target);
                }
                break;
            case 41:
                {
                    this.CompassBearing = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 42:
                {
                    this.textBlock = (global::Windows.UI.Xaml.Controls.TextBlock)(target);
                }
                break;
            case 43:
                {
                    this.textBox = (global::Windows.UI.Xaml.Controls.TextBox)(target);
                }
                break;
            case 44:
                {
                    this.SendButton = (global::Windows.UI.Xaml.Controls.Button)(target);
                    #line 16 "..\..\..\MainPage.xaml"
                    ((global::Windows.UI.Xaml.Controls.Button)this.SendButton).Click += this.SendButton_Click;
                    #line default
                }
                break;
            default:
                break;
            }
            this._contentLoaded = true;
        }

        [global::System.CodeDom.Compiler.GeneratedCodeAttribute("Microsoft.Windows.UI.Xaml.Build.Tasks"," 14.0.0.0")]
        [global::System.Diagnostics.DebuggerNonUserCodeAttribute()]
        public global::Windows.UI.Xaml.Markup.IComponentConnector GetBindingConnector(int connectionId, object target)
        {
            global::Windows.UI.Xaml.Markup.IComponentConnector returnValue = null;
            return returnValue;
        }
    }
}

