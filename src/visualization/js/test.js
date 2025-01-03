// 场景
var scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);

// 相机
var camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.set(0, 45, 20);

// 渲染器
var renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// 控制器
// 控制器
var controls = new THREE.TrackballControls(camera, renderer.domElement);
controls.rotateSpeed = 1.0;
controls.zoomSpeed = 1.2;
controls.panSpeed = 0.8;
controls.noZoom = false;
controls.noPan = true; // 禁用平移
controls.staticMoving = true; // 静止时阻尼会覆盖
controls.dynamicDampingFactor = 0.4; // 阻尼惯性
controls.enableDamping = true; // 启用阻尼效果


// 光源
var ambientLight = new THREE.AmbientLight(0x333333);
// 增加环境光亮度
ambientLight.intensity = 7;

scene.add(ambientLight);

var sunlight = new THREE.DirectionalLight(0xffffff, 1);
sunlight.position.set(5,3,5);
scene.add(sunlight);
// 删除定向光源
scene.remove(sunlight);

// 地球
var earthGeometry = new THREE.SphereGeometry(8, 64, 64);
//earthGeometry.rotateY(-Math.PI / 2); // 将贴图旋转以匹配地球的经纬度
var earthMaterial = new THREE.MeshPhongMaterial({
    color: 0xffffff,  // 设置为灰白色
     transparent: true,  // 开启透明
    opacity: 0.8,  // 设置透明度
    side: THREE.DoubleSide,  // 设置为双面可见
    map: new THREE.TextureLoader().load('jpg/8081_earthmap10k.jpg'),
    bumpMap: new THREE.TextureLoader().load('jpg/8081_earthbump10k.jpg'),
    bumpScale: 0.005,
    specularMap: new THREE.TextureLoader().load('jpg/8081_earthspec10k.jpg'),
    specular: new THREE.Color('grey')
});
var earth = new THREE.Mesh(earthGeometry, earthMaterial);
// 设置地球旋转，以使北极朝上
earth.rotation.x = - Math.PI / 2;
earth.rotation.y = 11.3 * Math.PI / 10;
scene.add(earth);

// 假设的地球模型半径为1个单位
var earthRadiusModel = 8;
// 实际地球半径
var earthRadiusReal = 6371; // 单位：公里
var orbitHeightMax = 2000; // 最大轨道高度，单位：公里

var scaleFactor = earthRadiusModel / (earthRadiusReal);



var satellitesData = []

// WebSocket连接
var ws = new WebSocket("ws://localhost:8080/ws");
ws.onmessage = function(event) {
    // 解析服务器发送的数据
    var data = JSON.parse(event.data);
    switch (data.type){
        case 'satellite-3D-position':
                // 更新卫星数据
            satellitesData = Object.values(data.data).filter(function(item) {
            return typeof item === 'object' && 'id' in item && 'x' in item && 'y' in item && 'z' in item;
             });
            //console.log(satellitesData);
            break
        case 'user-position':
            //console.log(data.data)
            // 提取用户的ID值
            clearUserPositions();
            drawUserPositions(data.data);
            // 重新渲染场景
            render();

            break
        case 'user-satellite-connection':
             // 根据传入的用户和卫星位置数据绘制连接线
            clearLines(scene);
            drawMultipleUserSatelliteLines(data.data, scene);
            render();
            //console.log(data.data)
            break
          // 添加其他case来处理更多的数据类型
        case 'network-delay':
            updateChart(data.data.time, data.data.delay)
            break
        case 'network-arrive-rate':
            updateChart2(data.data.time, data.data.arrive_rate)
            console.log(data.data)
            break
        case 'beijing':
            console.log(data.data)
            break
        default:
            console.log('Received unknown message type:', message.type);
    }

    // 更新场景中的卫星和轨道
    updateSatellitesAndOrbits(satellitesData);
};

// 绘制卫星和轨道
function drawSatellitesAndOrbits(satellitesData) {
    var orbitMaterials = {}; // 存储轨道材质
    var orbitCurves = {}; // 存储轨道曲线

    satellitesData.forEach(function (satellite) {
        // 绘制卫星
        var satGeometry = new THREE.SphereGeometry(0.05, 8, 8);
        var satMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
        var satelliteMesh = new THREE.Mesh(satGeometry, satMaterial);
        satelliteMesh.name = 'satellite'; // 添加这一行来标记卫星

        // 应用缩放因子调整卫星坐标
        var scaledPosition = scalePosition({x: satellite.x, y: satellite.y, z: satellite.z});
        satelliteMesh.position.set(scaledPosition.x, scaledPosition.y, scaledPosition.z);
        scene.add(satelliteMesh);

        // 收集同一轨道的卫星
        if (!orbitCurves[satellite.orbit_id]) {
            orbitCurves[satellite.orbit_id] = new THREE.CatmullRomCurve3([]);
            orbitMaterials[satellite.orbit_id] = new THREE.LineBasicMaterial({
                color: 0xBEBEBE,
                transparent: true,
                opacity: 0.6
            });
        }

        orbitCurves[satellite.orbit_id].points.push(
            new THREE.Vector3(scaledPosition.x, scaledPosition.y, scaledPosition.z)
        );
        //createSatelliteCone(scaledPosition, 2, 30);
    });

    // 绘制轨道
    for (var orbit_id in orbitCurves) {
        // 为了使轨道闭合，设置曲线为闭合
        orbitCurves[orbit_id].closed = true;

        // 使用曲线生成轨道几何体
        var points = orbitCurves[orbit_id].getPoints(150); // 通过点的数量可以控制曲线的平滑度
        var orbitGeometry = new THREE.BufferGeometry().setFromPoints(points);
        var orbit = new THREE.Line(orbitGeometry, orbitMaterials[orbit_id]);
        orbit.name = 'orbit'; // 添加这一行来标记轨道

        scene.add(orbit);
    }
}

// 缩放位置的辅助函数
function scalePosition(position) {
    return new THREE.Vector3(
        position.x * scaleFactor,
        position.y * scaleFactor,
        position.z * scaleFactor
    );
}
//绘制坐标轴
var axisLength = 20; // 坐标轴长度
var axisThickness = 0.03; // 坐标轴粗细
var axes = createAxes(axisLength, axisThickness);
scene.add(axes);

//绘制用户的代码

var userIds = [1,2];
function drawUserPositions(userPositions) {
    userPositions.forEach(function(user) {
        // Create a sphere geometry for the user marker
        var userGeometry = new THREE.SphereGeometry(0.03, 8, 8); // Size of user marker, adjust as needed
        var userMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 }); // Red color for the user marker

        // Create mesh with geometry and material
        var userMesh = new THREE.Mesh(userGeometry, userMaterial);
        userMesh.name = 'userPosition'; // Tagging the mesh
        // Set the position using ECI coordinates
        x = user.x * scaleFactor
        y = user.y * scaleFactor
        z = user.z * scaleFactor
        userMesh.position.set(x, y, z);

        // Optionally, scale the user position if needed (depends on your scene's scale)
        // userMesh.position.multiplyScalar(scaleFactor);

        // Add user mesh to the scene
        scene.add(userMesh);
        // 如果是指定的用户ID，则让标记闪烁
        if (userIds && userIds.indexOf(user.user_id) !== -1) {
            blinkMarker(userMesh);
        } else {
        }
    });
}
//用戶闪烁代码
function blinkMarker(marker) {
  var duration = 50000;
  var interval = 10;
  var originalOpacity = marker.material.opacity;
  var alpha = 0;
  var delta = 0.2;
  var blinkCount = 0;
  var startColor = new THREE.Color(0x800080);
  var endColor = new THREE.Color(0xff0000);
  var currentColor = new THREE.Color();
  var startScale = new THREE.Vector3(1, 1, 1);
  var endScale = new THREE.Vector3(2, 2, 2);
  var currentScale = new THREE.Vector3();

  // 创建波纹平面
  var rippleGeometry = new THREE.CircleGeometry(1, 32);
  var rippleMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000, transparent: true, opacity: 0, side: THREE.DoubleSide });
  var ripple = new THREE.Mesh(rippleGeometry, rippleMaterial);
  ripple.position.copy(marker.position);
  ripple.lookAt(camera.position); // 使平面面向相机方向
  scene.add(ripple);

  var blinkIntervalId = setInterval(function() {
    currentColor.lerpColors(startColor, endColor, alpha);
    marker.material.color.copy(currentColor);
    currentScale.lerpVectors(startScale, endScale, alpha);
    marker.scale.copy(currentScale);

    // 更新波纹效果
    rippleMaterial.opacity = alpha * 0.5;
    // 更新波纹颜色
    var rippleColor = new THREE.Color().lerpColors(startColor, endColor, alpha);
    rippleMaterial.color.set(rippleColor);
    alpha += delta;
    marker.material.opacity = 1 - alpha;
    renderer.render(scene, camera);

    if (alpha >= 1 || alpha <= 0) {
      delta = -delta;
      blinkCount++;
    }

    if (blinkCount >= duration / interval) {
      clearInterval(blinkIntervalId);
      marker.material.opacity = originalOpacity;
      rippleMaterial.opacity = 0;
      console.log("闪烁效果被执行");
      renderer.render(scene, camera);
    }
  }, interval);
}
// 绘制卫星-用户链接关系
function drawMultipleUserSatelliteLines(connections, scene) {
    connections.forEach(data => {
        // Create the line geometry
        var lineGeometry = new THREE.BufferGeometry();

        // Define vertices for the line using data from each pair
        const vertices = new Float32Array([
            data.user_x * scaleFactor, data.user_y * scaleFactor, data.user_z * scaleFactor, // User position
            data.satellite_x * scaleFactor, data.satellite_y * scaleFactor, data.satellite_z * scaleFactor // Satellite position
        ]);

        // Add vertices to the line geometry
        lineGeometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

        // Create a material for the line with a basic color
        var lineMaterial = new THREE.LineBasicMaterial({ color: 0x0000ff });

        // Create the line using the geometry and material
        var line = new THREE.Line(lineGeometry, lineMaterial);

        // Add the line to the scene
        scene.add(line);
    });
}

// 调用绘制函数
drawSatellitesAndOrbits(satellitesData);

// 更新卫星和轨道的函数
function updateSatellitesAndOrbits(satellitesData) {
    // 清除当前的卫星和轨道
    clearScene();
    //清除网络拓扑
    clearSatelliteConnections();
    // 绘制新的卫星和轨道
    drawSatellitesAndOrbits(satellitesData);

    // 重新渲染场景
    render();
}
// 创建坐标轴

drawSatellitesAndOrbits(satellitesData);
// 清除场景中的卫星和轨道的函数
function clearScene() {
    // 得到所有子对象的一个简单复制列表，因为我们在迭代时会修改它们
    var objectsToRemove = scene.children.filter(function(child) {
        // 这里我们假设所有的卫星和轨道对象都被赋予了一个自定义的name属性
        return child.name === 'satellite' || child.name === 'orbit';
    });

    // 对于这个列表中的每个对象，移除它并进行清理
    objectsToRemove.forEach(function(object) {
        // 移除轨道或卫星
        scene.remove(object);

        // 对于Geometry或BufferGeometry，需要调用dispose来释放内存
        if (object.geometry) {
            object.geometry.dispose();
        }

        // 对于Material，也需要调用dispose
        if (object.material) {
            if (object.material instanceof Array) {
                // 对于材质数组（如THREE.MeshFaceMaterial），需要遍历数组并释放每个材质
                object.material.forEach(function(material) {
                    material.dispose();
                });
            } else {
                // 单个材质可以直接释放
                object.material.dispose();
            }
        }
    });
}
function clearSatelliteConnections() {
    var connectionsToRemove = scene.children.filter(function(child) {
        return child.name === 'connection';
    });

    connectionsToRemove.forEach(function(connection) {
        scene.remove(connection);
        if (connection.geometry) {
            connection.geometry.dispose();
        }
        if (connection.material) {
            connection.material.dispose();
        }
    });
}
//清除场景中的用户
function clearUserPositions() {
    var removableObjects = [];
    scene.traverse((object) => {
        if (object.name === 'userPosition') {
            removableObjects.push(object);
        }
    });

    // Remove the objects outside of the traverse to avoid modifying the scene graph during traversal
    removableObjects.forEach((object) => {
        scene.remove(object);
        // Also dispose of the geometry and material to free up memory
        if (object.geometry) object.geometry.dispose();
        if (object.material) object.material.dispose();
    });
}

// 清除用户-卫星链接关系
function clearLines(scene) {
    // Temporary array to hold objects to be removed
    const objectsToRemove = [];

    // Iterate over all objects in the scene
    scene.traverse((object) => {
        // Check if the object is a line
        if (object instanceof THREE.Line) {
            objectsToRemove.push(object);
        }
    });

    // Remove the objects and dispose of their resources
    objectsToRemove.forEach((object) => {
        scene.remove(object); // Remove the line from the scene
        if (object.geometry) object.geometry.dispose(); // Dispose the geometry
        if (object.material) object.material.dispose(); // Dispose the material
    });
}

function createSatelliteCone(satellitePosition, distanceToSurface, coneAngle) {
    // 删除之前绘制的容器对象
    if (previousContainer !== null) {
      scene.remove(previousContainer);
      previousContainer = null;
    }
   // 创建容器对象
  var container = new THREE.Object3D();
  // 创建圆锥的材质
  var coneMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000, transparent: true, opacity: 0.3 });
  // 计算圆锥的高度和底面半径
  var coneHeight = 3;
  var coneRadius = Math.tan(THREE.Math.degToRad(coneAngle / 2)) * coneHeight;
  // 创建圆锥的几何体
  var coneGeometry = new THREE.ConeGeometry(coneRadius, coneHeight, 90,1, true, 0, Math.PI * 2, 0, 1, satellitePosition);
  var coneMesh = new THREE.Mesh(coneGeometry, coneMaterial);
  coneMesh.position.copy(satellitePosition);
  // 将圆锥体添加到容器对象中
  container.add(coneMesh);
  // 计算从卫星到地球原点的方向向量，并使其为单位向量
    var directionToEarthCenter = new THREE.Vector3(0, 0, 0).sub(satellitePosition).normalize();
   // 设置圆锥体的Z轴与这个方向向量对齐
    var originalZAxis = new THREE.Vector3(0, -1, 0);
    var quaternion = new THREE.Quaternion().setFromUnitVectors(originalZAxis, directionToEarthCenter);

    // 应用四元数旋转到圆锥体
    coneMesh.applyQuaternion(quaternion);

  container.name = "Cone";
  // 将当前容器对象添加到场景中
  scene.add(container);
  // 返回容器对象
  return container;
}
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    render();
}

function render() {
    renderer.render(scene, camera);
}
//绘制坐标轴
function createAxes(length, thickness) {
  var axisGroup = new THREE.Group();

  // X轴
  var xAxisGeometry = new THREE.CylinderGeometry(thickness, thickness, length);
  var xAxisMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
  var xAxis = new THREE.Mesh(xAxisGeometry, xAxisMaterial);
  xAxis.rotation.z = -Math.PI / 2;
  axisGroup.add(xAxis);

  // Y轴
  var yAxisGeometry = new THREE.CylinderGeometry(thickness, thickness, length);
  var yAxisMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
  var yAxis = new THREE.Mesh(yAxisGeometry, yAxisMaterial);
  yAxis.rotation.x = Math.PI / 2;
  axisGroup.add(yAxis);

  // Z轴
  var zAxisGeometry = new THREE.CylinderGeometry(thickness, thickness, length);
  var zAxisMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff });
  var zAxis = new THREE.Mesh(zAxisGeometry, zAxisMaterial);
  axisGroup.add(zAxis);

  return axisGroup;
}
var showConnections = false; // 初始状态显示连接线
//触发网络拓扑
function toggleSatelliteConnections() {
    showConnections = !showConnections; // 切换连接线的显示状态

    // 清除之前绘制的连接线
    scene.remove(scene.getObjectByName('connections'));

    // 如果需要显示连接线，则重新绘制
    if (showConnections) {
        satellitesData.forEach(satelliteA => {
            drawSatelliteConnections(satelliteA, satellitesData);
        });
    }
}
//绘制网络拓扑
function drawSatelliteConnections(satelliteA, satellites) {
     const curveMaterial = new THREE.LineBasicMaterial({
        color: 0x800080,     // 设置紫色
        linewidth: 1.5,        // 设置线宽
        linecap: 'round',    // 设置线帽为圆形，使线条末端平滑
        linejoin: 'round'    // 设置线连接为圆形，使线条转折处平滑
    });
      const connections = [
        { orbitId: satelliteA.orbit_id, satelliteId: satelliteA.satellite_id + 1 }, // B
        { orbitId: satelliteA.orbit_id, satelliteId: satelliteA.satellite_id - 1 }, // C
        { orbitId: satelliteA.orbit_id + 1, satelliteId: satelliteA.satellite_id }, // D
        { orbitId: satelliteA.orbit_id - 1, satelliteId: satelliteA.satellite_id }  // E
      ];
   var scaledPositionA = scalePosition({x: satelliteA.x, y: satelliteA.y, z: satelliteA.z});

  connections.forEach(connection => {
    const satelliteB = satellites.find(satellite => satellite.orbit_id === connection.orbitId && satellite.satellite_id === connection.satelliteId);

   if (satelliteB) {
      var scaledPositionB = scalePosition({x: satelliteB.x, y: satelliteB.y, z: satelliteB.z});
      const curve = new THREE.CatmullRomCurve3([
                new THREE.Vector3(scaledPositionA.x, scaledPositionA.y, scaledPositionA.z),
                new THREE.Vector3((scaledPositionA.x + scaledPositionB.x) / 2, (scaledPositionA.y + scaledPositionB.y) / 2, (scaledPositionA.z + scaledPositionB.z) / 2),
                new THREE.Vector3(scaledPositionB.x, scaledPositionB.y, scaledPositionB.z)
            ]);

            const points = curve.getPoints(150);
            const positions = [];
            points.forEach(point => {
                positions.push(point.x, point.y, point.z);
            });

            const positionsAttribute = new THREE.Float32BufferAttribute(positions, 3);

            const geometry = new THREE.BufferGeometry();
            geometry.setAttribute('position', positionsAttribute);

            const curveLine = new THREE.Line(geometry, curveMaterial);
            curveLine.name = 'connection';
            scene.add(curveLine); // 将连接线添加到场景中
    }
  });
}
// 开始动画循环
animate();

// 响应窗口大小变化
window.addEventListener('resize', function () {
    var width = window.innerWidth;
    var height = window.innerHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
});








