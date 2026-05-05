<center>

# BÁO CÁO ĐỒ ÁN MÔN HỌC
**(Đồ án phát triển ứng dụng)**  
**Lớp:** IT003.Q21.CTTN

</center>

## SINH VIÊN THỰC HIỆN

- **Mã sinh viên:** 25521516  
- **Họ và tên:** Dương Đăng Quang

**TÊN ĐỀ TÀI:** FANTASY TOWER DEFENSE 2D

---

## CÁC NỘI DUNG CẦN BÁO CÁO:

### I. Giới thiệu đồ án:

#### 1. Mô tả chung về ứng dụng:

- Ứng dụng là một tựa game chiến thuật Tower Defense được phát triển bằng ngôn ngữ Python kết hợp với thư viện Pygame. Trò chơi lấy bối cảnh thế giới fantasy với đồ họa Pixel Art mang phong cách Forest environment, kết hợp cùng giao diện UI hiện đại, sắc nét.

- Nhiệm vụ của người chơi là xây dựng các trụ phòng thủ Tower và các công trình Beacon trên một bản đồ dạng Grid nhằm ngăn chặn các đợt Wave ngày càng mạnh của kẻ địch.

- Trò chơi tích hợp nhiều cơ chế và hệ thống nâng cao nhằm đem lại trải nghiệm chiến thuật có chiều sâu:

    - **Hệ thống quản lý Inventory:** Hỗ trợ dạng cụộn, quản lý đa dạng các loại vật phẩm như tháp, trụ hỗ trợ và các loại ngọc Gem cường hóa.

    - **Hệ thống Adjacency Buff:** Các Beacon khi đặt xuống sẽ tự động tính toán và tăng cường sức mạnh tốc độ đánh và sát thương cho các tháp lân cận.

    - **Hệ thống quản lý VFX:** Tích hợp hệ thống Particle tạo các hiệu ứng cháy nổ, tia lửa và số sát thương nảy lên Floating Text một cách sinh động.

    - **Chế độ Auto-slotting:** Ứng dụng giải thuật Deterministic để tự động hỗ trợ người chơi phân bổ tài nguyên, mua và đặt tháp vào các vị trí chiến thuật tối ưu.

    - **Giao diện chiến thuật thời gian thực:** Các Tooltips và Stat comparisons được cập nhật liên tục dựa trên các thay đổi trên bản đồ.

#### 2. Các CTDL và giải thuật đã được sử dụng:

**a. CÁC CẤU TRÚC DỮ LIỆU:**

- **Mảng 2 chiều (2D Array):**

    - **Mục đích:** Dùng để biểu diễn bản đồ của trò chơi thành một ma trận các Grid cells. Mỗi ô lưu trữ trạng thái của nó như trống, có chướng ngại vật, loại địa hình, hoặc tham chiếu đến tháp đang chiếm đóng.

    - **Ý nghĩa:** Phù hợp tuyệt đối với cơ chế đặt tháp trên bản đồ dạng Tile-based map. Cho phép truy xuất trạng thái của một tọa độ trên bản đồ với thời gian O(1), từ đó kiểm tra tính hợp lệ khi người chơi đặt tháp hay các thuật toán tìm đường thực thi cực kỳ nhanh chóng.

- **Danh sách liên kết / Mảng động (List):**

    - **Mục đích:** Lưu trữ các Dynamic Entities trong game như danh sách kẻ địch đang sống, danh sách Projectiles đang bay, các Particles và Floating Text.

    - **Ý nghĩa:** Game loop thường xuyên phải duyệt qua toàn bộ các đối tượng này ở mỗi frame để update vị trí và render. List trong Python giúp dễ dàng thêm mới (append) hoặc loại bỏ (remove/pop) các thực thể vòng đời ngắn khi chúng được sinh ra hoặc bị tiêu diệt.

- **Bảng băm (Dictionary):**

    - **Mục đích:** Sử dụng cho Asset Manager để ánh xạ tên file thành các đối tượng Surface đã được nạp vào bộ nhớ. Đồng thời quản lý Inventory với key là loại item và value là số lượng hay thông số.

    - **Ý nghĩa:** Cho phép truy cập dữ liệu với thời gian trung bình là O(1). Tránh việc tải lại cùng một hình ảnh hay âm thanh nhiều lần, giúp tối ưu RAM và tăng tốc độ khởi tạo game.

- **Hàng đợi (Queue):**

    - **Mục đích:** Dùng trong Wave Manager để lưu trữ thứ tự xuất hiện của quái vật.

    - **Ý nghĩa:** Cơ chế First In First Out giúp quản lý việc spawn quái vật theo đúng thứ tự kịch bản một cách tự nhiên và chính xác.

**b. CÁC GIẢI THUẬT NỔI BẬT:**

- **Spatial Partitioning (Phân vùng không gian):**

    - **Mục đích:** Tối ưu hóa quá trình Collision Detection và tìm kiếm mục tiêu. Bản đồ được chia thành các zones lớn hơn kích thước ô cơ bản.

    - **Ý nghĩa:** Thay vì kiểm tra va chạm của một viên đạn với tất cả kẻ địch trên bản đồ theo cấp số nhân O(N * M), đạn và tháp chỉ cần truy vấn những kẻ địch đang nằm trong cùng một vùng hoặc các vùng lân cận kề nó. Điều này giảm độ phức tạp xuống gần bằng tuyến tính O(1) cho việc tra cứu, đảm bảo FPS luôn ổn định ở mức 60 trở lên.

- **Finite State Machine (Máy trạng thái hữu hạn):**

    - **Mục đích:** Quản lý luồng trạng thái của toàn bộ hệ thống game (Menu, Playing, Pause, Game Over) và logic AI của kẻ địch.

    - **Ý nghĩa:** Tránh hiện tượng Spaghetti Code. Mỗi trạng thái sở hữu hàm update riêng, giúp việc thêm các cơ chế mới như hiệu ứng đóng băng, làm chậm diễn ra vô cùng thuận lợi.

- **Thuật toán tìm đường Breadth-First Search (BFS):**

    - **Mục đích:** Tính toán và tìm ra đường đi ngắn nhất từ Spawn point của quái vật đến Base thông qua các ô có thể đi qua (walkable).

    - **Ý nghĩa:** Cực kỳ hiệu quả và đảm bảo tìm được đường đi tối ưu trên các đồ thị lưới không có trọng số. Thuật toán này giúp linh hoạt trong việc cấu hình bản đồ, quái vật luôn biết cách điều hướng vượt qua các vật cản một cách thông minh.

- **Giải thuật Deterministic Slotting:**

    - **Mục đích:** Tự động tính toán, phân tích lưới và quyết định việc xây tháp, nâng cấp trang bị trong chế độ Auto.

    - **Ý nghĩa:** Tính toán độ bao phủ (coverage) và tiềm năng nhận buff của từng ô trống. Thuật toán ưu tiên đặt Beacon tại các giao điểm có thể ảnh hưởng đến nhiều tháp nhất và tự động cắm các tháp gây sát thương vào những điểm nóng giao tranh.

- **Object Pooling (Hàng đợi tái sử dụng đối tượng):**

    - **Mục đích:** Áp dụng trong `VFXManager` cho cả `Particle` và `FloatingText`.

    - **Ý nghĩa:** Tránh việc liên tục tạo và hủy hàng trăm thực thể gây giật khung hình do thu gom rác (Garbage Collection). Hệ thống đưa các đối tượng hết hạn vào pool để tái chế.

### II. Quá trình thực hiện

#### 1. Tuần 1: Xây dựng nền tảng và Core Gameplay

- **Kiến trúc phần mềm:** Phân chia dự án thành các thư mục rõ ràng gồm Core xử lý engine, Entities gồm Tháp/Quái/Đạn, và Systems chứa logic hệ thống.

- **Core Loop và Môi trường:** Cài đặt Grid mang phong cách rừng xanh, khởi tạo cửa sổ Pygame 1080p, đồng bộ hóa 60 FPS.

- **Thực thể cơ bản:** Tạo và lập trình logic cho các class Tower, Enemy, Projectile.

- **Tương tác người dùng:** Triển khai cơ chế tương tác bằng chuột toàn diện, click để đặt tháp và hệ thống Tooltips.

- **Hệ thống AI cơ bản:** Thiết lập hệ thống di chuyển cho Enemy theo Waypoints tiến về Base.

- **Hệ thống Combat:** Cài đặt logic dò tìm mục tiêu cho Tower: Quét bán kính, chọn quái vật gần nhất, xoay nòng và bắn đạn.

#### 2. Tuần 2: Nâng cao, Tối ưu hóa và Hoàn thiện UI/UX

- **Nâng cấp Đồ họa Pixel Art:** Tích hợp hệ thống `AssetManager` nạp trực tiếp các texture Pixel Art chất lượng cao từ thư mục `assets/textures`.

- **Đồ họa và UI/UX:** Tái cấu trúc toàn bộ đồ họa sang phong cách Fantasy. Hoàn thiện các thành phần UI với nút bấm phong cách đá/gỗ, hệ thống Tooltip cập nhật thời gian thực.

- **Chiều sâu chiến thuật:** Lập trình Scrollable Inventory. Ra mắt Beacon và Hệ thống trang bị Gem cho phép gắn ngọc vào tháp.

- **Hiệu ứng Nghe và Nhìn:** Triển khai `VFXManager` tạo ra các mảnh vỡ nhỏ khi đạn nổ và Floating Text bay lên cho từng điểm sát thương.

- **Tự động hóa:** Hoàn thiện và tinh chỉnh chế độ Auto giúp game tự động chơi.

- **Cân bằng Game:** Tinh chỉnh các tham số máu, sát thương qua từng Wave để tạo thử thách tăng dần.

#### 3. Tuần 3: Tự động hóa Tài liệu và Chuẩn hóa Hệ thống

- **Hệ thống hóa Tài liệu Kỹ thuật (API Reference):** Tự động hóa quy trình trích xuất docstrings bằng công cụ `pdoc`. Toàn bộ tài liệu của các package (`core`, `entities`, `systems`, `main`) được tổng hợp thành một cổng HTML tĩnh hoàn chỉnh tại thư mục `docs/`.

- **Tự động hóa báo cáo đa định dạng:** Tích hợp quy trình tự động chuyển đổi tài liệu từ Markdown sang định dạng Word (.docx) bằng Pandoc để báo cáo tiến độ.

### III. Kết quả đạt được

- Hoàn thành engine Tower Defense bằng Pygame ở độ phân giải 1080p cực kỳ tối ưu và ổn định.

- Gameplay sở hữu chiều sâu chiến thuật vượt trội nhờ sự kết hợp giữa Adjacency Buff và Hệ thống Gem.

- Giao diện thân thiện, nhất quán với phong cách đồ họa Fantasy tươi sáng. Phản hồi trực quan từ Tooltips và VFX.

- Mã nguồn được kiến trúc theo tiêu chuẩn OOP sạch sẽ, dễ đọc, dễ dàng mở rộng trong tương lai.

- Chế độ Auto hoạt động mượt mà, phân bổ vị trí cực kỳ trực quan và hợp lý.

### IV. Tài liệu tham khảo

- Pygame Official Documentation.

- Game Programming Patterns (Robert Nystrom).

- Tài nguyên Pixel Art từ cộng đồng OpenGameArt và Itch.io.

---

### V. Phụ lục 1: Giới thiệu (demo) kết quả

**Demo video:** https://youtu.be/srJkNt6Z0R8

*(Các hình ảnh minh họa bao gồm: Màn hình đầu game, Tiếng Việt, Bên trong trò chơi, Các loại tháp, Kho đồ, Màn hình thất bại, Cơ chế nâng cấp)*

---

### VI. Phụ lục 2: docstring

**Link GitHub:** https://github.com/rquq/tower-defense-2d-pygame.git

Dưới đây là tập hợp đầy đủ docstrings của các thành phần cốt lõi:

#### a. Hệ thống Tối ưu Không gian (SpatialManager)

```python
class SpatialManager:
    """Quản lý việc phân vùng không gian để tối ưu hóa kiểm tra va chạm Spatial Hashing."""
    def get_nearby_entities(self, x: float, y: float, radius: float) -> list:
        """Truy xuất nhanh danh sách các entities nằm trong vùng lân cận."""
        pass
```

#### b. Hệ thống Tìm đường (Pathfinding)

```python
def get_path_bfs(start_grid: tuple, end_grid: tuple, walkable_grid: set) -> list:
    """Thuật toán tìm đường Breadth-First Search (BFS) trên lưới không trọng số."""
    pass
```

#### c. Thực thể Tháp phòng thủ (Tower)

```python
class Tower:
    """Đại diện cho công trình phòng thủ. Tự động bắn kẻ địch và nhận các nâng cấp."""
    def recalculate(self, adjacency_buffs: list) -> None:
        """Tính toán lại toàn bộ chỉ số sau khi nhận Buff từ Beacon hoặc Gem."""
        pass
```

#### d. Thực thể Kẻ địch (Enemy)

```python
class Enemy:
    """Đại diện cho quái vật tấn công căn cứ."""
    def take_damage(self, amount: float, fire_mod: bool = False, ice_mod: bool = False) -> None:
        """Trừ máu kẻ địch và kích hoạt các hiệu ứng trạng thái."""
        pass
```

#### e. Quản lý Tài nguyên (AssetManager)

```python
class AssetManager:
    """Singleton quản lý nạp và lưu trữ Assets (hình ảnh, âm thanh)."""
    def _extract_sprites(self, path: str, expected_count: int) -> list:
        """Cắt sprite sheet và khử màu nền trắng."""
        pass
```

#### f. Quản lý Hiệu ứng (VFXManager)

```python
class VFXManager:
    """Xử lý hạt nổ Particle và chữ nổi FloatingText sử dụng Object Pooling."""
    def create_explosion(self, x: float, y: float, color: tuple, count: int = 15) -> None:
        """Tạo hiệu ứng nổ tung tóe các hạt."""
        pass
```
