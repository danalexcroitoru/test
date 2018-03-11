var exec = require('sync-exec');
var username = "pinbox01@mail.com";
var password = "MyP@ym3nt$!";
var sender = "danalex.croitoru@gmail.com";
var timeout = "60";

var pin = exec('python c:\\testscripts\\getpin.py email=' + username + ' password=' + password + ' sender=' + sender + ' timeout=' + timeout).stdout
console.log(pin);
