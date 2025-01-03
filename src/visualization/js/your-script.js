


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
var controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.1;
controls.enableZoom = true;
controls.screenSpacePanning = false; // 确保不是在屏幕空间中平移
controls.autoRotate = false; // 如果需要，关闭自动旋转
controls.enableRotate = true; // 允许旋转


// 光源
var ambientLight = new THREE.AmbientLight(0x333333);
scene.add(ambientLight);

var sunlight = new THREE.DirectionalLight(0xffffff, 1);
sunlight.position.set(5,3,5);
scene.add(sunlight);

// 地球
var earthGeometry = new THREE.SphereGeometry(8, 64, 64);
//earthGeometry.rotateY(-Math.PI / 2); // 将贴图旋转以匹配地球的经纬度
var earthMaterial = new THREE.MeshPhongMaterial({
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


// 卫星数据
//var satellitesData = [{"id": 0, "x": 7512.315196207192, "y": 566.2057254401026, "z": 751.3803759171157, "orbit_id": 0}, {"id": 1, "x": 6035.440720388983, "y": 2750.8606138647838, "z": 3650.5153326288028, "orbit_id": 0}, {"id": 2, "x": 2941.3747775766337, "y": 4198.424622313813, "z": 5571.497654005171, "orbit_id": 0}, {"id": 3, "x": -940.8301615246488, "y": 4521.024143730916, "z": 5999.60167835896, "orbit_id": 0}, {"id": 4, "x": -4570.940418630557, "y": 3632.218896873712, "z": 4820.117278088057, "orbit_id": 0}, {"id": 5, "x": -6976.270881913632, "y": 1770.1635298661324, "z": 2349.0863457301566, "orbit_id": 0}, {"id": 6, "x": -7512.3151962071925, "y": -566.2057254401016, "z": -751.3803759171144, "orbit_id": 0}, {"id": 7, "x": -6035.440720388982, "y": -2750.860613864784, "z": -3650.5153326288037, "orbit_id": 0}, {"id": 8, "x": -2941.374777576636, "y": -4198.4246223138125, "z": -5571.497654005169, "orbit_id": 0}, {"id": 9, "x": 940.8301615246479, "y": -4521.024143730916, "z": -5999.60167835896, "orbit_id": 0}, {"id": 10, "x": 4570.940418630559, "y": -3632.2188968737114, "z": -4820.117278088056, "orbit_id": 0}, {"id": 11, "x": 6976.270881913631, "y": -1770.1635298661347, "z": -2349.0863457301593, "orbit_id": 0}, {"id": 12, "x": 5557.997757197938, "y": 5029.5000280315635, "z": 1064.345526139513, "orbit_id": 1}, {"id": 13, "x": 2956.1109297408184, "y": 5778.302242592609, "z": 3897.7778751894143, "orbit_id": 1}, {"id": 14, "x": -437.86343407716834, "y": 4978.8130376280205, "z": 5686.803790306414, "orbit_id": 1}, {"id": 15, "x": -3714.5126443390604, "y": 2845.254899965458, "z": 5952.055222296563, "orbit_id": 1}, {"id": 16, "x": -5995.861191275106, "y": -50.68699040354108, "z": 4622.458264166903, "orbit_id": 1}, {"id": 17, "x": -6670.623574079879, "y": -2933.04734262715, "z": 2054.27734710715, "orbit_id": 1}, {"id": 18, "x": -5557.997757197939, "y": -5029.500028031562, "z": -1064.3455261395109, "orbit_id": 1}, {"id": 19, "x": -2956.1109297408184, "y": -5778.302242592609, "z": -3897.7778751894143, "orbit_id": 1}, {"id": 20, "x": 437.8634340771676, "y": -4978.8130376280205, "z": -5686.803790306414, "orbit_id": 1}, {"id": 21, "x": 3714.512644339061, "y": -2845.2548999654578, "z": -5952.055222296563, "orbit_id": 1}, {"id": 22, "x": 5995.861191275108, "y": 50.686990403544584, "z": -4622.4582641669, "orbit_id": 1}, {"id": 23, "x": 6670.623574079879, "y": 2933.0473426271496, "z": -2054.277347107151, "orbit_id": 1}, {"id": 24, "x": 1293.336262174957, "y": 7332.009625743761, "z": 1374.3933792565122, "orbit_id": 2}, {"id": 25, "x": -1255.7893202280252, "y": 6216.922661246692, "z": 4134.3568795253495, "orbit_id": 2}, {"id": 26, "x": -3468.4271684122787, "y": 3436.016290261827, "z": 5786.522792703312, "orbit_id": 2}, {"id": 27, "x": -4751.702757814298, "y": -265.5678708788782, "z": 5888.194596592139, "orbit_id": 2}, {"id": 28, "x": -4761.763430587236, "y": -3895.9933354819354, "z": 4412.129413446801, "orbit_id": 2}, {"id": 29, "x": -3495.9134375862723, "y": -6482.490532125573, "z": 1753.8377170667884, "orbit_id": 2}, {"id": 30, "x": -1293.3362621749573, "y": -7332.009625743761, "z": -1374.3933792565117, "orbit_id": 2}, {"id": 31, "x": 1255.7893202280268, "y": -6216.922661246691, "z": -4134.35687952535, "orbit_id": 2}, {"id": 32, "x": 3468.427168412277, "y": -3436.0162902618304, "z": -5786.522792703311, "orbit_id": 2}, {"id": 33, "x": 4751.702757814297, "y": 265.5678708788758, "z": -5888.194596592139, "orbit_id": 2}, {"id": 34, "x": 4761.763430587237, "y": 3895.993335481934, "z": -4412.129413446801, "orbit_id": 2}, {"id": 35, "x": 3495.9134375862764, "y": 6482.490532125569, "z": -1753.8377170667945, "orbit_id": 2}, {"id": 36, "x": -3451.864687948333, "y": 6525.335676658052, "z": 1680.6741156538817, "orbit_id": 3}, {"id": 37, "x": -4745.536613965098, "y": 3974.138534208136, "z": 4359.603899030129, "orbit_id": 3}, {"id": 38, "x": -4767.645836617588, "y": 358.07418090774536, "z": 5870.381338341678, "orbit_id": 3}, {"id": 39, "x": -3512.2682075507932, "y": -3353.9358599973134, "z": 5808.194838781843, "orbit_id": 3}, {"id": 40, "x": -1315.7811486692558, "y": -6167.261495750307, "z": 4189.707222687798, "orbit_id": 3}, {"id": 41, "x": 1233.2684064143043, "y": -7328.07439420545, "z": 1448.590939751714, "orbit_id": 3}, {"id": 42, "x": 3451.8646879483326, "y": -6525.335676658054, "z": -1680.6741156538806, "orbit_id": 3}, {"id": 43, "x": 4745.536613965097, "y": -3974.1385342081353, "z": -4359.603899030129, "orbit_id": 3}, {"id": 44, "x": 4767.645836617589, "y": -358.074180907748, "z": -5870.381338341677, "orbit_id": 3}, {"id": 45, "x": 3512.2682075507937, "y": 3353.9358599973125, "z": -5808.194838781843, "orbit_id": 3}, {"id": 46, "x": 1315.7811486692544, "y": 6167.261495750309, "z": -4189.707222687796, "orbit_id": 3}, {"id": 47, "x": -1233.2684064143018, "y": 7328.07439420545, "z": -1448.5909397517173, "orbit_id": 3}, {"id": 48, "x": -6664.566698248468, "y": 2995.644701148014, "z": 1982.3482411224695, "orbit_id": 4}, {"id": 49, "x": -6032.688844863623, "y": 123.60315506501846, "z": 4572.901547280017, "orbit_id": 4}, {"id": 50, "x": -3784.3568873093286, "y": -2781.557756599587, "z": 5938.149576776853, "orbit_id": 4}, {"id": 51, "x": -522.0095579293425, "y": -4941.402513682809, "z": 5712.275222641119, "orbit_id": 4}, {"id": 52, "x": 2880.2098109391372, "y": -5777.202457747601, "z": 3955.8013356543856, "orbit_id": 4}, {"id": 53, "x": 5510.679286934281, "y": -5065.005668747827, "z": 1139.373675361102, "orbit_id": 4}, {"id": 54, "x": 6664.566698248468, "y": -2995.6447011480154, "z": -1982.3482411224677, "orbit_id": 4}, {"id": 55, "x": 6032.688844863623, "y": -123.60315506501846, "z": -4572.901547280017, "orbit_id": 4}, {"id": 56, "x": 3784.3568873093295, "y": 2781.5577565995864, "z": -5938.149576776853, "orbit_id": 4}, {"id": 57, "x": 522.0095579293418, "y": 4941.4025136828095, "z": -5712.275222641119, "orbit_id": 4}, {"id": 58, "x": -2880.2098109391404, "y": 5777.202457747601, "z": -3955.801335654383, "orbit_id": 4}, {"id": 59, "x": -5510.67928693428, "y": 5065.005668747828, "z": -1139.3736753611029, "orbit_id": 4}, {"id": 60, "x": -7012.834499230896, "y": -1717.0398849612088, "z": 2278.5888878534774, "orbit_id": 5}, {"id": 61, "x": -4646.74163048994, "y": -3597.21473794558, "z": 4773.665190247302, "orbit_id": 5}, {"id": 62, "x": -1035.558094423129, "y": -4513.5188068961, "z": 5989.641759977799, "orbit_id": 5}, {"id": 63, "x": 2853.1023967598744, "y": -4220.429156516126, "z": 5600.698657170518, "orbit_id": 5}, {"id": 64, "x": 5977.276404807769, "y": -2796.478921934892, "z": 3711.0528721243227, "orbit_id": 5}, {"id": 65, "x": 7499.8440272498165, "y": -623.2144185705454, "z": 827.0334669232155, "orbit_id": 5}, {"id": 66, "x": 7012.834499230896, "y": 1717.0398849612088, "z": -2278.5888878534774, "orbit_id": 5}, {"id": 67, "x": 4646.741630489936, "y": 3597.2147379455823, "z": -4773.665190247305, "orbit_id": 5}, {"id": 68, "x": 1035.558094423133, "y": 4513.518806896099, "z": -5989.641759977799, "orbit_id": 5}, {"id": 69, "x": -2853.1023967598717, "y": 4220.429156516127, "z": -5600.698657170519, "orbit_id": 5}, {"id": 70, "x": -5977.276404807768, "y": 2796.4789219348922, "z": -3711.0528721243236, "orbit_id": 5}, {"id": 71, "x": -7499.844027249815, "y": 623.2144185705498, "z": -827.0334669232215, "orbit_id": 5}, {"id": 72, "x": -4407.2269605051315, "y": -5594.530126679607, "z": 2568.5840808256507, "orbit_id": 6}, {"id": 73, "x": -1303.54082431896, "y": -5568.292609768876, "z": 4961.3445487415165, "orbit_id": 6}, {"id": 74, "x": 2149.428023044476, "y": -4050.035584850387, "z": 6024.716751449541, "orbit_id": 6}, {"id": 75, "x": 5026.45936744432, "y": -1446.5747956539258, "z": 5473.770965980404, "orbit_id": 6}, {"id": 76, "x": 6556.654983549608, "y": 1544.49454182922, "z": 3456.1326706238915, "orbit_id": 6}, {"id": 77, "x": 6330.000191763283, "y": 4121.717814114951, "z": 512.4264172388868, "orbit_id": 6}, {"id": 78, "x": 4407.226960505132, "y": 5594.530126679607, "z": -2568.5840808256494, "orbit_id": 6}, {"id": 79, "x": 1303.5408243189595, "y": 5568.292609768876, "z": -4961.344548741517, "orbit_id": 6}, {"id": 80, "x": -2149.4280230444733, "y": 4050.0355848503877, "z": -6024.71675144954, "orbit_id": 6}, {"id": 81, "x": -5026.45936744432, "y": 1446.5747956539262, "z": -5473.770965980404, "orbit_id": 6}, {"id": 82, "x": -6556.654983549609, "y": -1544.494541829222, "z": -3456.1326706238897, "orbit_id": 6}, {"id": 83, "x": -6330.000191763283, "y": -4121.717814114949, "z": -512.4264172388902, "orbit_id": 6}, {"id": 84, "x": -19.43572732245004, "y": -7013.443433355164, "z": 2851.5389633723707, "orbit_id": 7}, {"id": 85, "x": 2445.434400894933, "y": -4996.728883724727, "z": 5135.425206686462, "orbit_id": 7}, {"id": 86, "x": 4255.052356249234, "y": -1641.144864902982, "z": 6043.278413078486, "orbit_id": 7}, {"id": 87, "x": 4924.532468994406, "y": 2154.182595131999, "z": 5331.8400490496915, "orbit_id": 7}, {"id": 88, "x": 4274.488083571687, "y": 5372.298568452181, "z": 3191.7394497061173, "orbit_id": 7}, {"id": 89, "x": 2479.0980680994735, "y": 7150.911478856726, "z": 196.41484236322955, "orbit_id": 7}, {"id": 90, "x": 19.435727322451967, "y": 7013.443433355165, "z": -2851.538963372369, "orbit_id": 7}, {"id": 91, "x": -2445.434400894936, "y": 4996.728883724723, "z": -5135.425206686464, "orbit_id": 7}, {"id": 92, "x": -4255.052356249234, "y": 1641.1448649029828, "z": -6043.278413078486, "orbit_id": 7}, {"id": 93, "x": -4924.532468994406, "y": -2154.1825951320016, "z": -5331.8400490496915, "orbit_id": 7}, {"id": 94, "x": -4274.488083571684, "y": -5372.298568452185, "z": -3191.7394497061127, "orbit_id": 7}, {"id": 95, "x": -2479.098068099474, "y": -7150.911478856726, "z": -196.41484236323032, "orbit_id": 7}, {"id": 96, "x": 4243.287154566788, "y": -5434.927778669859, "z": 3126.67797582853, "orbit_id": 8}, {"id": 97, "x": 4924.385595491737, "y": -2242.518316214583, "z": 5295.4300210989095, "orbit_id": 8}, {"id": 98, "x": 4285.998892885223, "y": 1550.7721180823912, "z": 6045.275868640314, "orbit_id": 8}, {"id": 99, "x": 2499.1822481694257, "y": 4928.53441569449, "z": 5175.294929156192, "orbit_id": 8}, {"id": 100, "x": 42.71173831843481, "y": 6985.699896752252, "z": 2918.5978928117843, "orbit_id": 8}, {"id": 101, "x": -2425.203347322312, "y": 7171.052731909072, "z": -120.13509194271953, "orbit_id": 8}, {"id": 102, "x": -4243.287154566788, "y": 5434.927778669859, "z": -3126.67797582853, "orbit_id": 8}, {"id": 103, "x": -4924.385595491737, "y": 2242.518316214584, "z": -5295.4300210989095, "orbit_id": 8}, {"id": 104, "x": -4285.998892885225, "y": -1550.7721180823874, "z": -6045.275868640314, "orbit_id": 8}, {"id": 105, "x": -2499.1822481694285, "y": -4928.534415694487, "z": -5175.294929156194, "orbit_id": 8}, {"id": 106, "x": -42.71173831843555, "y": -6985.699896752251, "z": -2918.5978928117847, "orbit_id": 8}, {"id": 107, "x": 2425.2033473223087, "y": -7171.052731909073, "z": 120.13509194271491, "orbit_id": 8}, {"id": 108, "x": 6572.58311018192, "y": -1614.641503166285, "z": 3393.2469812856657, "orbit_id": 9}, {"id": 109, "x": 5081.676804257561, "y": 1375.858543790056, "z": 5440.920429904354, "orbit_id": 9}, {"id": 110, "x": 2229.139302436421, "y": 3997.69840503839, "z": 6030.703643248173, "orbit_id": 9}, {"id": 111, "x": -1220.6942752890354, "y": 5548.3582070735, "z": 5004.564685592215, "orbit_id": 9}, {"id": 112, "x": -4343.443807745499, "y": 5612.339908204675, "z": 2637.456661962509, "orbit_id": 9}, {"id": 113, "x": -6302.371079546597, "y": 4172.499663283445, "z": -436.3557443121388, "orbit_id": 9}, {"id": 114, "x": -6572.58311018192, "y": 1614.641503166286, "z": -3393.246981285665, "orbit_id": 9}, {"id": 115, "x": -5081.67680425756, "y": -1375.8585437900563, "z": -5440.920429904354, "orbit_id": 9}, {"id": 116, "x": -2229.139302436423, "y": -3997.6984050383885, "z": -6030.703643248173, "orbit_id": 9}, {"id": 117, "x": 1220.694275289035, "y": -5548.358207073501, "z": -5004.564685592216, "orbit_id": 9}, {"id": 118, "x": 4343.443807745501, "y": -5612.339908204675, "z": -2637.456661962507, "orbit_id": 9}, {"id": 119, "x": 6302.371079546597, "y": -4172.499663283446, "z": 436.3557443121369, "orbit_id": 9}]
//;
var satellitesData = []

// WebSocket连接
var ws = new WebSocket("ws://localhost:8080/ws");


ws.onmessage = function(event) {
    // 解析服务器发送的数据
    var data = JSON.parse(event.data);
    switch (data.type){
        case 'satellite-3D-position':
        console.log(data.data)
                // 更新卫星数据
            satellitesData = Object.values(data.data).filter(function(item) {
            return typeof item === 'object' && 'id' in item && 'x' in item && 'y' in item && 'z' in item;
             });
            //console.log(satellitesData);
            break
        case 'user-position':
            //console.log(data.data)
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


//绘制用户的代码
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
    });
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

    // 绘制新的卫星和轨道
    drawSatellitesAndOrbits(satellitesData);

    // 重新渲染场景
    render();
}

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


function animate() {
    requestAnimationFrame(animate);
    controls.update();
    render();
}

function render() {
    renderer.render(scene, camera);
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








