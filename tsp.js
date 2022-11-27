// This code originally based off David Hacker's TSP code
// https://dmhacker.github.io/sim/tsp
// added fixed star system import, labels, solution output
window.onload = function () {
  var scene, camera, renderer, labelRenderer;
  var controls;
  var options, gui;
  var info;
  var starsWeakMap;

  init();
  animate();

  function init() {

    info = document.createElement('div');
    info.style.position = 'absolute';
    info.style.zIndex = 1;
    info.style.color = "white";
    info.style.top = 150 + 'px';
    info.style.left = 10 + 'px';
    document.body.appendChild(info);

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

    renderer = new THREE.WebGLRenderer({
      antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x000000);


    labelRenderer = new THREE.CSS2DRenderer();
    labelRenderer.setSize(window.innerWidth, window.innerHeight);
    labelRenderer.domElement.style.position = 'absolute';
    labelRenderer.domElement.style.top = '0px';
    document.body.appendChild(labelRenderer.domElement);

    document.body.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, labelRenderer.domElement);
    controls.minDistance = 5;
    controls.maxDistance = 100;

    controls.target.position = new THREE.Vector3(0, 0, 0);

    var SimulationOptions = function () {
      this.cities = 30;
      this.temperature = 300;
      this.reset = reset;
      this.rerun = rerun;
      this.show_sa = true;
      this.show_naive = true;
      this.show_debug = false;
      this.pause = false;
    };

    options = new SimulationOptions();
    gui = new dat.GUI();
    gui.add(options, 'temperature', 100, 500);
    gui.add(options, 'show_sa');
    gui.add(options, 'show_naive');
    gui.add(options, 'show_debug');
    gui.add(options, 'pause');
    gui.add(options, 'reset');
    gui.add(options, 'rerun');

    camera.position.x = 0;
    camera.position.y = 0;
    camera.position.z = -100;

    reset();

    window.addEventListener('resize', function () {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
      labelRenderer.setSize(window.innerWidth, window.innerHeight);
    }, false);
  }

  var cities;
  var original_score;
  var sa_solution, sa_score, current_sa_solution, current_sa_score;
  var hc_solution, hc_score;
  var lines;
  var T, ratio, iteration;

  function reset() {
    for (var i = scene.children.length - 1; i >= 0; i--) {
      obj = scene.children[i];
      scene.remove(obj);
    }

    var labels = document.querySelectorAll('.label');
    for (let index = 0; index < labels.length; index++) {
      const element = labels[index];
      element.remove();
    }

    cities = [];
    lines = {};
    var dotGeometry = new THREE.Geometry();

    starsWeakMap = new WeakMap();
    starKeys = Object.keys(stars);
    starCount = starKeys.length;

    for (var i = 0; i < starCount; i++) {
      var starKey = starKeys[i];
      var starObj = stars[starKey];

      var x = starObj["x"];
      var y = starObj["y"];
      var z = starObj["z"];
      var vec = new THREE.Vector3(x, y, z);

      for (var j in cities) {
        var other = cities[j];
        var material = new THREE.LineBasicMaterial({
          transparent: true
        });
        var geometry = new THREE.Geometry();
        geometry.vertices.push(vec);
        geometry.vertices.push(new THREE.Vector3(other[0], other[1], other[2]));

        var line = new THREE.Line(geometry, material);
        scene.add(line);

        var merged = [x, y, z, other[0], other[1], other[2]];
        var reverseMerged = [other[0], other[1], other[2], x, y, z];
        lines[merged] = line;
        lines[reverseMerged] = line;
      }

      starPos = [x, y, z];
      cities.push(starPos);

      // Fold index into the object
      starObj["idx"] = i;

      starsWeakMap.set(starPos, starObj)

      dotGeometry.vertices.push(vec);
    }

    // Labels

    labelMaterial = new THREE.PointsMaterial({ color: 0xFFFFFF });
    labelMaterial.color.setHSL(1.0, 0.3, 0.7);

    var labels = new THREE.Points(geometry, labelMaterial);
    scene.add(labels);

    for (var i = 0; i < starCount; i++) {
      var starKey = starKeys[i];
      var starObj = stars[starKey];

      var labelDiv = document.createElement('div');
      labelDiv.className = 'label';
      console.log(`Star -> ${starObj["name"]}`);
      labelDiv.textContent = `${starObj["name"]}`;
      labelDiv.style.marginTop = '-1em';
      var labelElement = new THREE.CSS2DObject(labelDiv);

      var x = starObj["x"];
      var y = starObj["y"];
      var z = starObj["z"];

      labelElement.position.set(x, y, z);
      labels.add(labelElement);
    }

    // Carry on...

    var dotMaterial = new THREE.PointsMaterial({
      size: 1.5,
      sizeAttenuation: true,
      color: 0xffffff
    });
    var dots = new THREE.Points(dotGeometry, dotMaterial);
    scene.add(dots);

    sa_solution = cities.slice();
    rerun();
  }

  function rerun() {
    shuffle(sa_solution);
    sa_score = distance(sa_solution);

    current_sa_solution = sa_solution;
    current_sa_score = sa_score;

    original_score = sa_score;

    hc_solution = sa_solution;
    hc_score = sa_score;

    T = options.temperature;
    ratio = 0.997;
    iteration = 0;

    calculate_naive();
  }

  function shuffle(a) {
    var j, x, i;
    for (i = a.length; i; i--) {
      j = Math.floor(Math.random() * i);
      x = a[i - 1];
      a[i - 1] = a[j];
      a[j] = x;
    }
  }

  function distance(proposed_solution) {
    var dist = 0;
    for (var i = 0; i < proposed_solution.length; i++) {
      var j = i + 1;
      if (j === proposed_solution.length) {
        break;
      }
      var a = proposed_solution[i];
      var b = proposed_solution[j];
      var dx = a[0] - b[0];
      var dy = a[1] - b[1];
      var dz = a[2] - b[2];
      dist += Math.sqrt(dx * dx + dy * dy + dz * dz);
    }
    return dist;
  }

  function clear_lines() {
    for (var k in lines) {
      if (lines.hasOwnProperty(k)) {
        var line = lines[k];
        line.visible = options.show_debug;
        line.material.opacity = 0.2;
        line.material.color.setHex(0xffffff);
      }
    }
  }

  function draw_solution(solution, opacity, color) {
    for (var i = 0; i < solution.length; i++) {
      var a = solution[i];
      var n = i + 1;
      if (n === solution.length) {
        break;
      }
      var b = solution[n];
      var c = a.slice();
      c.push(b[0]);
      c.push(b[1]);
      c.push(b[2]);
      var line = lines[c];
      line.visible = true;
      line.material.opacity = opacity;
      line.material.color.setHex(color);
    }
  }

  function calculate_naive() {
    // Usually takes about 1000-10000 iterations to solve
    for (var k = 0; k < 10000; k++) {
      var new_hc_solution = hc_solution.slice();
      var o = Math.floor(Math.random() * new_hc_solution.length);
      var p = Math.floor(Math.random() * new_hc_solution.length);
      var tmp = new_hc_solution[p];
      new_hc_solution[p] = new_hc_solution[o];
      new_hc_solution[o] = tmp;
      var new_hc_score = distance(new_hc_solution);
      if (new_hc_score < hc_score) {
        hc_solution = new_hc_solution;
        hc_score = new_hc_score;
      }
    }
  }

  last_swapped = "";

  function animate() {
    solution = "";

    if (T <= 1) {
      clear_lines();
      if (options.show_naive)
        draw_solution(hc_solution, 1.0, 0xff0000);
      if (options.show_sa)
        draw_solution(sa_solution, 1.0, 0xffff00);

      routeIndices = [];
      starKeys = Object.keys(stars);
      solution = "<br><br><b>Final route:</b><br>"
      for (let i = 0; i < sa_solution.length; i++) {
        var elem = sa_solution[i];
        var starObj = starsWeakMap.get(elem);
        solution += `${starObj["idx"]} ${starObj["name"]}<br>`;
        routeIndices.push(starObj["idx"]);
      }
      solution += "<br>" + routeIndices;

    } else if (!options.pause) {
      for (var k = 0; k < 1000; k++) {
        var new_sa_solution = current_sa_solution.slice();
        var i = Math.floor(Math.random() * new_sa_solution.length);
        var j = Math.floor(Math.random() * new_sa_solution.length);
        last_swapped = `(${i}-${j})`;
        tmp = new_sa_solution[i];
        new_sa_solution[i] = new_sa_solution[j];
        new_sa_solution[j] = tmp;
        var new_sa_score = distance(new_sa_solution);
        var accept_probability = Math.exp((current_sa_score - new_sa_score) / T);
        if (Math.random() < accept_probability) {
          current_sa_solution = new_sa_solution;
          current_sa_score = new_sa_score;
          if (new_sa_score < sa_score) {
            sa_solution = new_sa_solution;
            sa_score = new_sa_score;
          }
        }

        iteration++;
      }

      T *= ratio;

      clear_lines();
      if (options.show_sa)
        draw_solution(current_sa_solution, 1.0, 0x008800);
      if (options.show_naive)
        draw_solution(hc_solution, 1.0, 0xff0000);
      if (options.show_sa)
        draw_solution(sa_solution, 1.0, 0xffff00);

      starKeys = Object.keys(stars);
      solution = "<br><br><b>Current best route:</b><br>"
      for (let i = 0; i < sa_solution.length; i++) {
        var elem = sa_solution[i];
        var starObj = starsWeakMap.get(elem);
        solution += `${starObj["idx"]} ${starObj["name"]}<br>`;
      }
    } else {
      // paused
      starKeys = Object.keys(stars);
      solution = `<br><br><b>Current route ${last_swapped}:</b><br>`;
      for (let i = 0; i < current_sa_solution.length; i++) {
        var elem = current_sa_solution[i];
        var starObj = starsWeakMap.get(elem);
        solution += `${starObj["idx"]} ${starObj["name"]}<br>`;
      }

    }

    infoText = "";

    infoText += "<b>Iteration:<br></b>" + iteration;
    infoText += "<br><br>";
    infoText += "<b>SA temperature:<br></b>" + T;
    infoText += "<br><br>";
    infoText += "<b>Original score:</b><br>" + original_score;
    infoText += "<br><br>";
    infoText += "<b>Naive score (red):</b><br>" + hc_score;
    infoText += "<br><br>";
    infoText += "<b>SA current score (dark green):</b><br>" + current_sa_score;
    infoText += "<br><br>";
    infoText += "<b>SA best score (yellow):</b><br>" + sa_score;
    infoText += solution;

    info.innerHTML = infoText;

    controls.update();

    renderer.render(scene, camera);
    labelRenderer.render(scene, camera);

    requestAnimationFrame(animate);
  }

};
