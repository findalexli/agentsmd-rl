#!/usr/bin/env bash
set -euo pipefail

cd /workspace/robotics-agent-skills

# Idempotency guard
if grep -qF "\"camera/image_raw\", sensor_qos, [this](const std::shared_ptr<const sensor_msgs::" "skills/ros2/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/ros2/SKILL.md b/skills/ros2/SKILL.md
@@ -122,6 +122,7 @@ if __name__ == '__main__':
 ```cpp
 #include <rclcpp/rclcpp.hpp>
 #include <sensor_msgs/msg/image.hpp>
+#include <vision_msgs/msg/detection2_d.hpp>
 #include <memory>
 
 class PerceptionNode : public rclcpp::Node {
@@ -137,25 +138,26 @@ public:
         auto reliable_qos = rclcpp::QoS(10).reliable();
 
         // Publishers and subscribers
-        det_pub_ = this->create_publisher<DetectionArray>("detections", reliable_qos);
+        det_pub_ = this->create_publisher<vision_msgs::msg::Detection2D>("detections", reliable_qos);
         image_sub_ = this->create_subscription<sensor_msgs::msg::Image>(
-            "camera/image_raw", sensor_qos,
-            std::bind(&PerceptionNode::image_callback, this, std::placeholders::_1));
+            "camera/image_raw", sensor_qos, [this](const std::shared_ptr<const sensor_msgs::msg::Image>& msg){
+                this->image_callback(msg);
+            });
 
         timer_ = this->create_wall_timer(
             std::chrono::milliseconds(static_cast<int>(1000.0 / rate_hz)),
-            std::bind(&PerceptionNode::timer_callback, this));
+            [this](){ this->timer_callback(); });
 
         RCLCPP_INFO(this->get_logger(), "Perception node started at %.1fHz", rate_hz);
     }
 
 private:
-    void image_callback(const sensor_msgs::msg::Image::SharedPtr msg) {
+    void image_callback(const std::shared_ptr<const sensor_msgs::msg::Image>& msg) {
         // Use shared_ptr for zero-copy potential
     }
     void timer_callback() {}
 
-    rclcpp::Publisher<DetectionArray>::SharedPtr det_pub_;
+    rclcpp::Publisher<vision_msgs::msg::Detection2D>::SharedPtr det_pub_;
     rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr image_sub_;
     rclcpp::TimerBase::SharedPtr timer_;
 };
@@ -443,14 +445,18 @@ public:
         sub_ = this->create_subscription<sensor_msgs::msg::Image>(
             "camera/image_raw",
             rclcpp::SensorDataQoS(),
-            std::bind(&PerceptionComponent::callback, this,
-                      std::placeholders::_1),
+            [this](sensor_msgs::msg::Image::UniquePtr msg) {
+                this->callback(std::move(msg));
+            },
             sub_options);
     }
 
 private:
-    void callback(const sensor_msgs::msg::Image::UniquePtr msg) {
-        // UniquePtr = zero-copy when using intra-process
+    void callback(sensor_msgs::msg::Image::UniquePtr msg) {
+        // UniquePtr = zero-copy when:
+        //   - publisher also uses UniquePtr
+        //   - both subscriber and publisher use intra-process
+        //   - this is the only subscriber
         // msg is moved, not copied
     }
 
PATCH

echo "Gold patch applied."
