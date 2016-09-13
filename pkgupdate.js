#!/usr/bin/env node
'use strict';

var fs = require('fs');

var pkgPath = process.argv[2];
var dataPath = process.argv[3];
var targetStr = process.argv[4] || 'dependencies';

fs.readFile(pkgPath, 'utf-8', function (err, data) {
  if (err) throw err;

  var pkg = JSON.parse(data.toString());

  if (!pkg[targetStr]) pkg[targetStr] = {};
  var target = pkg[targetStr];

  fs.readFile(dataPath, 'utf-8', function (err, data) {
    if (err) throw err;

    var content = JSON.parse(data.toString());

    for (var prop in content) {
      target[prop] = content[prop];
    }

    fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2), 'utf-8');
    console.log('\n\tpackage.json updated');
  });
});