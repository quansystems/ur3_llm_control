# UR3e điều khiển bằng ngôn ngữ tự nhiên (LLM) — Dự án sinh viên

Dự án `ur3_llm_control` là bản triển khai riêng của **Nguyen Van Quan** cho thiết bị UR3/UR3e trong mô phỏng Gazebo. Hệ thống nhận lệnh tiếng Việt / tiếng Anh, dùng LLM qua **9Router** để lập kế hoạch, kiểm tra bằng validator rồi điều khiển robot qua **MoveIt 2**.

Môi trường: **Ubuntu 22.04** (hoặc Windows 11 + WSL2 Ubuntu 22.04), **ROS 2 Humble**, **Gazebo Classic**.

Quy ước: workspace là `~/ur3_ws`. Dòng bắt đầu bằng `#` là chú thích. Mọi cài đặt và chạy được tối ưu để phù hợp với phiên bản workspace hiện tại của dự án này.

---

## 1. Cài đặt phần mềm

### 1.1 ROS 2 Humble

Làm theo hướng dẫn chính thức: https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html

```bash
sudo apt update && sudo apt install -y ros-humble-desktop ros-dev-tools
```

### 1.2 Gazebo Classic, MoveIt 2, ros2_control, UR

```bash
sudo apt install -y \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-gazebo-ros2-control \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-moveit \
  ros-humble-ur \
  ros-humble-xacro \
  python3-yaml python3-numpy git

sudo rosdep init     # báo "already exists" thì bỏ qua
rosdep update
```

### 1.3 Tạo workspace, cài `Universal_Robots_ROS2_Gazebo_Simulation` và build

> Gói này **không có trên apt** cho Humble, phải clone từ source (nhánh `humble`).

```bash
mkdir -p ~/ur3_ws/src && cd ~/ur3_ws/src

# Gói mô phỏng UR cho Gazebo Classic
git clone -b humble https://github.com/UniversalRobots/Universal_Robots_ROS2_Gazebo_Simulation.git

# Gói điều khiển LLM: chép thư mục ur3_llm_control (trong ur3epro/src/) vào ~/ur3_ws/src
cp -r /đường/dẫn/tới/ur3epro/src/ur3_llm_control ~/ur3_ws/src/

cd ~/ur3_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

Kết quả mong đợi: `Summary: 2 packages finished`.

Tự động source mỗi khi mở terminal:

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "source ~/ur3_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

Kiểm tra:

```bash
ros2 pkg prefix ur3_llm_control
ros2 pkg prefix ur_simulation_gazebo
```

### 1.4 Sửa thông tin sinh viên

```bash
nano ~/ur3_ws/src/ur3_llm_control/config/student_config.yaml
```

Điền đúng `student_name`, `student_id` (thứ tự vùng A/B/C được tính tự động từ 2 chữ số cuối MSSV). Sau khi sửa:

```bash
cd ~/ur3_ws && colcon build --symlink-install && source install/setup.bash
```

---

## 2. Khởi tạo 9Router và lấy API key

9Router là proxy OpenAI-compatible chạy local (cổng `20128`), gói dùng nó để gọi LLM.

### 2.1 Cài 9Router (cần Node.js ≥ 18)

Ubuntu 22.04 mặc định có Node quá cũ, cài bằng nvm:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 22
node -v                  # phải là v22.x
npm install -g 9router
```

### 2.2 Chạy 9Router lần đầu và cấu hình

```bash
9router --no-browser
```

Mở trình duyệt: **http://localhost:20128**

1. Đăng nhập bằng mật khẩu mặc định `123456` (đổi mật khẩu khi được hỏi).
2. Vào **Providers** → thêm một provider LLM (ví dụ **Gemini** với API key lấy ở https://aistudio.google.com/app/apikey) → lưu và bấm test.
3. Vào **Endpoint** → tạo / copy **API key của 9Router** (dạng `sk-...`).
   Đây là key dùng để code gọi 9Router, **không phải** key của nhà cung cấp LLM.

### 2.3 Chọn model

Model được đặt trong `config/student_config.yaml` (mục `llm.model`), hoặc ghi đè bằng biến môi trường:

```bash
export NINEROUTER_MODEL="gemini/gemini-2.5-flash"     # ví dụ
```

Xem danh sách model đang có trong 9Router:

```bash
curl -s http://localhost:20128/v1/models | python3 -m json.tool | grep '"id"'
```

> Tên model phải đúng với tên hiển thị trong 9Router. Không điền API key vào file yaml, hãy dùng biến môi trường ở mục 3.

---

## 3. Vận hành (mỗi lần chạy)

Cần **3 terminal**, mở theo đúng thứ tự.

### Terminal 1 — 9Router

```bash
9router --no-browser
```

Để nguyên terminal này chạy suốt buổi.

### Terminal 2 — Vào workspace và chạy mô phỏng

```bash
cd ~/ur3_ws
source install/setup.bash
ros2 launch ur3_llm_control sim.launch.py
```

Đợi đến khi log hiện `You can start planning now!` và RViz hiện robot (lần đầu có thể mất 1–2 phút).

Tuỳ chọn:

```bash
ros2 launch ur3_llm_control sim.launch.py gazebo_gui:=false   # máy yếu / WSL2: tắt cửa sổ Gazebo
ros2 launch ur3_llm_control sim.launch.py ur_type:=ur3        # dùng UR3 thay vì UR3e
```

### Terminal 3 — Khai báo API key và chạy node điều khiển

```bash
cd ~/ur3_ws
source install/setup.bash
export NINEROUTER_API_KEY="sk-key-cua-ban"
ros2 run ur3_llm_control llm_robot_node --ros-args -p use_sim_time:=true
```

Thay `sk-key-cua-ban` bằng API key 9Router ở mục 2.2. Khi thấy dấu nhắc `Command>` là có thể nhập lệnh.

---

## 4. Sử dụng

```
Command> Put the red cube in zone B.
Command> Đưa vật màu đỏ sang vùng B.
Command> Hãy lấy khối màu vàng và đặt nó vào ô A.
Command> Arrange all objects according to my student ID.
Command> state        # xem trạng thái hiện tại
Command> quit         # thoát
```

Lệnh sai luật (ví dụ `Move the green cube to zone A.`) sẽ bị `TASK REJECTED`, robot đứng yên.

Các cách chạy khác của node:

```bash
# Chạy đúng 1 lệnh rồi thoát
ros2 run ur3_llm_control llm_robot_node --ros-args -p use_sim_time:=true -p command:="Move the blue cube to zone C."

# Chỉ lập và kiểm tra kế hoạch, robot KHÔNG chạy
ros2 run ur3_llm_control llm_robot_node --ros-args -p use_sim_time:=true -p dry_run:=true

# Đổi model khi chạy
ros2 run ur3_llm_control llm_robot_node --ros-args -p use_sim_time:=true -p llm_model:=<ten-model>
```

Muốn làm lại từ đầu: `quit` rồi chạy lại lệnh ở Terminal 3 (khối được đặt lại vị trí ban đầu).

---

## 5. Kiểm tra nhanh trước khi demo (không cần Gazebo)

```bash
~/ur3_ws/src/ur3_llm_control/tools/run_all_checks.sh     # cuối cùng in: ALL CHECKS PASSED
ros2 run ur3_llm_control check_scene                     # mọi vị trí gắp/đặt đều với tới được
ros2 run ur3_llm_control offline_cli "Move the blue cube to zone C."   # thử LLM thật + robot giả lập
```

---

## 6. Tắt hệ thống

`Ctrl+C` ở Terminal 3, rồi Terminal 2, rồi Terminal 1. Nếu Gazebo còn treo:

```bash
pkill -9 -f gzserver; pkill -9 -f gzclient
```

---

## 7. Xử lý sự cố thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| `Package 'ur3_llm_control' not found` | Chưa `source ~/ur3_ws/install/setup.bash` trong terminal đó. |
| `no 9Router API key` | Chưa `export NINEROUTER_API_KEY=...` trong Terminal 3. |
| `cannot reach 9Router at http://localhost:20128/...` | Terminal 1 chưa chạy `9router`. Với WSL2, cài 9Router ngay trong WSL. |
| `9Router HTTP 401` | Sai API key. Phải dùng key 9Router (Endpoint), không phải key nhà cung cấp LLM. |
| `9Router HTTP 400/404 ... model` | Tên model sai, kiểm tra bằng lệnh `curl .../v1/models` ở mục 2.3. |
| `9Router HTTP 429` / quota | Hết hạn mức của provider. Đợi 1–2 phút hoặc đổi model. |
| `[setup] ERROR: not available: ['/move_action' ...]` | MoveIt chưa lên. Đợi `You can start planning now!` ở Terminal 2 rồi chạy lại node. |
| Robot trong RViz và Gazebo lệch nhau | Quên `-p use_sim_time:=true` khi chạy node. |
| Gazebo đen màn hình / crash (WSL2, máy ảo) | `export LIBGL_ALWAYS_SOFTWARE=1` rồi chạy lại Terminal 2, hoặc dùng `gazebo_gui:=false`. |
| Spawner timeout / controller không active | Tắt hết (mục 6), chạy lại với `gazebo_gui:=false`. |
| `LLM PLAN: REJECTED BY VALIDATOR` với lệnh hợp lệ | Model trả sai định dạng, thử model mạnh hơn, giữ `temperature: 0`. |