/*
 * @Author: Ceoifung
 * @Date: 2022-02-18 09:45:43
 * @LastEditTime: 2022-02-18 16:30:40
 * @LastEditors: Ceoifung
 * @Description: 子进程处理工具库
 * XiaoRGEEK All Rights Reserved, Powered by Ceoifung
 */

var execTest = require("child_process")

class ProcessUtils{

    static execShell = (cmd, callback) => {
        try {
            var child = execTest.exec(cmd)
            child.stdout.on("data", stdout => {
                callback(null, stdout, null)
            })
            child.stderr.on("data", stderr => {
                callback(null, null, stderr)
            })
            child.on("error", err => {
                callback(err, null, null)
            })
            return child.pid
        } catch (e) {
            callback(e)
            return null
        }

    }
}

module.exports = ProcessUtils