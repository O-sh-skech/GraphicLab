import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js"; 


  const canvas = document.getElementById("three-canvas");
  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
  const savedPos = sessionStorage.getItem("cameraPosition0");

  if (savedPos) {
    const { x, y, z } = JSON.parse(savedPos);
    camera.position.set(x, y, z);
  } else {
    camera.position.set(0, 0, 3); // 初回は初期位置
  }
  //カメラ位置の保存
  window.addEventListener("beforeunload", () => {
    const pos = camera.position;
    sessionStorage.setItem("cameraPosition1", JSON.stringify({ x: pos.x, y: pos.y, z: pos.z }));
  });

  const renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    preserveDrawingBuffer: true  // ←これが重要
  });
  
  renderer.setClearColor(0xE88A10, 1); 
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);

  // カメラ操作
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  

  // 補助オブジェクト
  scene.add(new THREE.AxesHelper(20));
  scene.add(new THREE.GridHelper(20, 10));

  // 球体
  const sphere = new THREE.Mesh(
    new THREE.SphereGeometry(0.1, 16, 16),
    new THREE.MeshStandardMaterial({ color: 0x00ff00 })
  );
  scene.add(sphere);

  // ライト
  const light = new THREE.DirectionalLight(0xffffff, 1);
  light.position.set(1, 1, 1);
  scene.add(light);

  fetch("static/Json/animation.json")
    .then(response => {
      if (!response.ok) {
        alert("JSONの読み込みに失敗しました");
      }
      return response.json();
    })
    .then(data => {
      const rawArray = data;
      const path = [];

      for (let i = 0; i < rawArray.length; i += 7) {
        const x = rawArray[i];
        const y = rawArray[i + 1];
        const z = rawArray[i + 2];
        path.push(new THREE.Vector3(x, y, z));
      }

    

        let currentIndex = 0;
        let trailPoints = [];
        let trailLine = null;
        const speed = 1.2;
        let hasLooped = false; 

        function animate() {
        requestAnimationFrame(animate);

         // カメラ操作のスムーズさに必要
        controls.update();  

        const target = path[currentIndex];
        const current = sphere.position;

        const dx = target.x - current.x;
        const dy = target.y - current.y;
        const dz = target.z - current.z;
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

        if (dist < 0.01) {
          trailPoints.push(current.clone());

            // 最後の点に到達したら遷移（1回だけ）
            if (currentIndex === path.length - 1 && !hasLooped) {
            hasLooped = true;
            setTimeout(() => {
              window.location.href = "/"; // draw.htmlを表示するルートに変更
            }, 1000); // 少し遅延してから遷移（1秒後）
          }
          currentIndex = (currentIndex + 1) % path.length;
        } else {
          current.x += dx * speed;
          current.y += dy * speed;
          current.z += dz * speed;
          trailPoints.push(current.clone());
        }

        updateLine();
        renderer.render(scene, camera);
        }

        function updateLine() {
            if (trailLine) {
            scene.remove(trailLine);
            }

        const geometry = new THREE.BufferGeometry().setFromPoints(trailPoints);
        const material = new THREE.LineBasicMaterial({ color: 0xff0000 });
        trailLine = new THREE.Line(geometry, material);
        scene.add(trailLine);
        }

        animate();

        window.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
         window.location.href = "/";  // Flaskでdraw.htmlを返すルートにしておく
        }
        });

      window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });
    })
    .catch(err => {
      console.error("エラー:", err);
    });