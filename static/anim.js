import { initThree } from "./base.js";
import { zoom } from './base.js';  
import * as THREE from "three";

const { canvas, scene, camera, renderer, controls } = initThree("three-canvas", "cameraPosition0");

  // Three.js のレンダラーと canvas サイズを同期させる
  const resizeCanvas = () => {
    const width = window.innerWidth * 0.7;  // 80vw 相当
    const height = window.innerHeight * 0.6; // 60vh 相当

    canvas.width = width;
    canvas.height = height;

    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };

  // 最初の描画時
  resizeCanvas();

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

        // ウィンドウサイズ変更時にも対応
        window.addEventListener('resize', resizeCanvas);

    })
    .catch(err => {
      console.error("エラー:", err);
    });

    // イベントリスナー登録（ID指定で明確）
    document.addEventListener("DOMContentLoaded", () => {
      document.getElementById("zoomInBtn").addEventListener("click", () => {
        zoom(-1, camera, controls);
      });
    
      document.getElementById("zoomOutBtn").addEventListener("click", () => {
        zoom(1, camera, controls);
      });
    });