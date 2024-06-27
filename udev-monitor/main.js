/*
 * @Author: Ceoifung
 * @Date: 2022-03-30 13:53:34
 * @LastEditTime: 2022-09-12 13:45:13
 * @LastEditors: Ceoifung
 * @Description: 小R科技USB摄像头mjpeg-streamer守护程序
 * XiaoRGEEK All Rights Reserved, Powered by Ceoifung
 */

var usbDetect = require('usb-detection');
const utils = require("./processUtils")

usbDetect.startMonitoring();
let pythonSocketScript = "python /home/pi/work/hexapod/src/xrtsclient.py"
let xrcameraScript = "./xrcamera.sh"
let offlineMsg = JSON.stringify({
    "type": "gui",
    "data": "camera offline"
})
let onlineMsg = JSON.stringify({
    "type": "gui",
    "data": "camera online"
})
// 480p摄像头
let vendorId = 911;     //0x038f
let productId = 24577; //0x6001
// 720P摄像头
let highVendorId = 3141;
let highProductId = 25447;
// 新摄像头
let newVendorId1 = 52225;
let newProductId1 = 52225;
let newVendorId2 = 52226;
let newProductId2 = 52226;
let newVendorId3 = 52227;
let newProductId3 = 52227;
let newVendorId4 = 52228;
let newProductId4 = 52228;
let newVendorId5 = 52229;
let newProductId5 = 52229;

/**
 * 开启摄像头
 */
function startCamera(){
    utils.execShell(`${pythonSocketScript} '${onlineMsg}'`, (err, stdout, stderr) => {
        console.log(err, stdout, stderr)
    })
    utils.execShell(`${xrcameraScript} start`, (err, stdout, stderr) => {
        if (err) console.log("err==>", err)
        else if (stdout) console.log("stdout==>", stdout)
        else {
            console.log("stderr==>", stderr)
        }
    })
}
/**
 * 停止摄像头
 */
function stopCamera(){
    utils.execShell(`${pythonSocketScript} '${offlineMsg}'`, (err, stdout, stderr) => {
        console.log(err, stdout, stderr)
    })
    utils.execShell(`${xrcameraScript} stop`, (err, stdout, stderr) => {
        if (err) console.log("err==>", err)
        else if (stdout) console.log("stdout==>", stdout)
        else {
            console.log("stderr==>", stderr)
        }
    })
}


// 开机首先启动摄像头画面
utils.execShell(`${xrcameraScript} start`, (err, stdout, stderr) => {
    if (err) console.log("err==>", err)
    else if (stdout) console.log("stdout==>", stdout)
    else {
        console.log("stderr==>", stderr)
    }
})
usbDetect.on(`add:${vendorId}:${productId}`, function (device) {
    // status = "heartbeat"
    console.log("xrcamera online", device)
    startCamera()
});


usbDetect.on(`remove:${vendorId}:${productId}`, function (device) {
    console.log("xrcamera offline, now start talking to app")
    stopCamera()
});


usbDetect.on(`add:${highVendorId}:${highProductId}`, function (device) {
    // status = "heartbeat"
    console.log("xrcamera online", device)
    startCamera()
    // utils.execShell(`${pythonSocketScript} '${onlineMsg}'`, (err, stdout, stderr) => {
    //     console.log(err, stdout, stderr)
    // })
    // utils.execShell(`${xrcameraScript} start`, (err, stdout, stderr) => {
    //     if (err) console.log("err==>", err)
    //     else if (stdout) console.log("stdout==>", stdout)
    //     else {
    //         console.log("stderr==>", stderr)
    //     }
    // })
});


usbDetect.on(`remove:${highVendorId}:${highProductId}`, function (device) {
    console.log("xrcamera offline, now start talking to app")
    stopCamera()
    // utils.execShell(`${pythonSocketScript} '${offlineMsg}'`, (err, stdout, stderr) => {
    //     console.log(err, stdout, stderr)
    // })
    // utils.execShell(`${xrcameraScript} stop`, (err, stdout, stderr) => {
    //     if (err) console.log("err==>", err)
    //     else if (stdout) console.log("stdout==>", stdout)
    //     else {
    //         console.log("stderr==>", stderr)
    //     }
    // })
});
// CC01
usbDetect.on(`add:${newVendorId1}:${newProductId1}`, function (device) {
    // status = "heartbeat"
    console.log("xrcamera online", device)
    startCamera()
});


usbDetect.on(`remove:${newVendorId1}:${newProductId1}`, function (device) {
    console.log("xrcamera offline, now start talking to app")
    stopCamera()
});
// CC02
usbDetect.on(`add:${newVendorId2}:${newProductId2}`, function (device) {
    // status = "heartbeat"
    console.log("xrcamera online", device)
    startCamera()
});


usbDetect.on(`remove:${newVendorId2}:${newProductId2}`, function (device) {
    console.log("xrcamera offline, now start talking to app")
    stopCamera()
});
// CC03
usbDetect.on(`add:${newVendorId3}:${newProductId3}`, function (device) {
    // status = "heartbeat"
    console.log("xrcamera online", device)
    startCamera()
});


usbDetect.on(`remove:${newVendorId3}:${newProductId3}`, function (device) {
    console.log("xrcamera offline, now start talking to app")
    stopCamera()
});
// CC04
usbDetect.on(`add:${newVendorId4}:${newProductId4}`, function (device) {
    // status = "heartbeat"
    console.log("xrcamera online", device)
    startCamera()
});


usbDetect.on(`remove:${newVendorId4}:${newProductId4}`, function (device) {
    console.log("xrcamera offline, now start talking to app")
    stopCamera()
});
// CC05
usbDetect.on(`add:${newVendorId5}:${newProductId5}`, function (device) {
    // status = "heartbeat"
    console.log("xrcamera online", device)
    startCamera()
});


usbDetect.on(`remove:${newVendorId5}:${newProductId5}`, function (device) {
    console.log("xrcamera offline, now start talking to app")
    stopCamera()
});
// // Detect add or remove (change)
// usbDetect.on('change', function (device) { console.log('change', device); });
// usbDetect.on('change:vid', function (device) { console.log('change', device); });
// usbDetect.on('change:vid:pid', function (device) { console.log('change', device); });

// // Get a list of USB devices on your system, optionally filtered by `vid` or `pid`
// usbDetect.find(function (err, devices) { console.log('find', devices, err); });
// usbDetect.find(vid, function (err, devices) { console.log('find', devices, err); });
// usbDetect.find(vid, pid, function (err, devices) { console.log('find', devices, err); });
// // Promise version of `find`:
// usbDetect.find().then(function (devices) { console.log(devices); }).catch(function (err) { console.log(err); });

// Allow the process to exit
// usbDetect.stopMonitoring()