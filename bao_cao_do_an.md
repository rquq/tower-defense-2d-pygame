# BÁO CÁO ĐỒ ÁN GAME FANTASY TOWER DEFENSE 2D

## 1. Giới thiệu đồ án

### a. Mô tả chung về ứng dụng
Ứng dụng là một tựa game chiến thuật Tower Defense được phát triển bằng ngôn ngữ Python kết hợp với thư viện Pygame. Trò chơi lấy bối cảnh thế giới fantasy với đồ họa Pixel Art mang phong cách Forest environment, kết hợp cùng giao diện UI hiện đại, sắc nét.

Nhiệm vụ của người chơi là xây dựng các trụ phòng thủ Tower và các công trình Beacon trên một bản đồ dạng Grid nhằm ngăn chặn các đợt Wave ngày càng mạnh của kẻ địch. Trò chơi tích hợp nhiều cơ chế và hệ thống nâng cao nhằm đem lại trải nghiệm chiến thuật có chiều sâu:
- Hệ thống quản lý Inventory: Hỗ trợ dạng cuộn, quản lý đa dạng các loại vật phẩm như tháp, trụ hỗ trợ và các loại ngọc Gem cường hóa.
- Hệ thống Adjacency Buff: Các Beacon khi đặt xuống sẽ tự động tính toán và tăng cường sức mạnh tốc độ đánh và sát thương cho các tháp lân cận.
- Hệ thống quản lý VFX: Tích hợp hệ thống Particle tạo các hiệu ứng cháy nổ, tia lửa và số sát thương nảy lên Floating Text một cách sinh động.
- Chế độ Auto-slotting: Ứng dụng giải thuật Deterministic để tự động hỗ trợ người chơi phân bổ tài nguyên, mua và đặt tháp vào các vị trí chiến thuật tối ưu.
- Giao diện chiến thuật thời gian thực: Các Tooltips và Stat comparisons được cập nhật liên tục dựa trên các thay đổi trên bản đồ.

### b. Các Cấu trúc dữ liệu và Giải thuật đã được sử dụng

**CÁC CẤU TRÚC DỮ LIỆU:**

1. Mảng 2 chiều 2D Array:
   - Mục đích: Dùng để biểu diễn bản đồ của trò chơi thành một ma trận các Grid cells. Mỗi ô lưu trữ trạng thái của nó như trống, có chướng ngại vật, loại địa hình, hoặc tham chiếu đến tháp đang chiếm đóng.
   - Ý nghĩa: Phù hợp tuyệt đối với cơ chế đặt tháp trên bản đồ dạng Tile-based map. Cho phép truy xuất trạng thái của một tọa độ trên bản đồ với thời gian O(1), từ đó kiểm tra tính hợp lệ khi người chơi đặt tháp hay các thuật toán tìm đường thực thi cực kỳ nhanh chóng.

2. Danh sách List:
   - Mục đích: Lưu trữ các Dynamic Entities trong game như danh sách kẻ địch đang sống, danh sách Projectiles đang bay, các Particles và Floating Text.
   - Ý nghĩa: Game loop thường xuyên phải duyệt qua toàn bộ các đối tượng này ở mỗi frame để update vị trí và render. List trong Python giúp dễ dàng thêm mới append hoặc loại bỏ bằng hàm remove hay pop các thực thể vòng đời ngắn khi chúng được sinh ra hoặc bị tiêu diệt.

3. Bảng băm Dictionary:
   - Mục đích: Sử dụng cho Asset Manager để ánh xạ tên file thành các đối tượng Surface đã được nạp vào bộ nhớ. Đồng thời quản lý Inventory với key là loại item và value là số lượng hay thông số.
   - Ý nghĩa: Cho phép truy cập dữ liệu với thời gian trung bình là O(1). Tránh việc tải lại cùng một hình ảnh hay âm thanh nhiều lần, giúp tối ưu RAM và tăng tốc độ khởi tạo game.

4. Hàng đợi Queue:
   - Mục đích: Dùng trong Wave Manager để lưu trữ thứ tự xuất hiện của quái vật.
   - Ý nghĩa: Cơ chế First In First Out giúp quản lý việc spawn quái vật theo đúng thứ tự kịch bản một cách tự nhiên và chính xác.

**CÁC GIẢI THUẬT NỔI BẬT:**

1. Thuật toán Spatial Partitioning:
   - Mục đích: Tối ưu hóa quá trình Collision Detection và tìm kiếm mục tiêu. Bản đồ được chia thành các zones lớn hơn kích thước ô cơ bản.
   - Ý nghĩa: Thay vì kiểm tra va chạm của một viên đạn với tất cả kẻ địch trên bản đồ theo cấp số nhân O(N * M), đạn và tháp chỉ cần truy vấn những kẻ địch đang nằm trong cùng một vùng hoặc các vùng lân cận kề nó. Điều này giảm độ phức tạp xuống gần bằng tuyến tính O(1) cho việc tra cứu, đảm bảo FPS luôn ổn định ở mức 60 trở lên với những Wave cao chứa hàng trăm kẻ địch.

2. Máy trạng thái Finite State Machine:
   - Mục đích: Quản lý luồng trạng thái của toàn bộ hệ thống game từ Main Menu qua Playing qua Pause đến Game Over và logic AI của kẻ địch từ Di chuyển qua Tấn công căn cứ qua Bị choáng đến Bị tiêu diệt.
   - Ý nghĩa: Tránh hiện tượng Spaghetti Code với quá nhiều khối lệnh if/else lồng nhau. Finite State Machine cung cấp cấu trúc rõ ràng, mỗi trạng thái sở hữu hàm update riêng, giúp việc thêm các cơ chế mới như hiệu ứng đóng băng, làm chậm diễn ra vô cùng thuận lợi.

3. Thuật toán tìm đường Breadth-First Search:
   - Mục đích: Tính toán và tìm ra đường đi ngắn nhất từ Spawn point của quái vật đến Base thông qua các ô có thể đi qua walkable.
   - Ý nghĩa: Cực kỳ hiệu quả và đảm bảo tìm được đường đi tối ưu trên các đồ thị lưới không có trọng số. Thuật toán này giúp linh hoạt trong việc cấu hình bản đồ, quái vật luôn biết cách điều hướng vượt qua các vật cản một cách thông minh.

4. Giải thuật Deterministic Slotting:
   - Mục đích: Trái tim của chế độ Auto, tự động tính toán, phân tích lưới và quyết định việc xây tháp, nâng cấp trang bị.
   - Ý nghĩa: Tính toán độ bao phủ coverage và tiềm năng nhận buff của từng ô trống. Thuật toán ưu tiên đặt Beacon tại các giao điểm có thể ảnh hưởng đến nhiều tháp nhất và tự động cắm các tháp gây sát thương vào những điểm nóng giao tranh.
3. Object Pooling (Hàng đợi tái sử dụng đối tượng):
   - Mục đích: Áp dụng trong `VFXManager` cho cả `Particle` và `FloatingText`.
   - Ý nghĩa: Thay vì liên tục tạo và hủy hàng trăm thực thể hiệu ứng gây giật khung hình do thu gom rác (Garbage Collection), hệ thống đưa các đối tượng hết hạn vào pool để tái chế.

**CÁC CHỈNH SỬA VÀ TỐI ƯU NÂNG CAO TRONG TUẦN 2:**

1. Tinh chỉnh thuật toán Spatial Partitioning:
   - Chỉnh sửa: Bổ sung các bộ lọc chiến thuật (Targeting Modes: First, Closest, Strongest) kết hợp cùng truy vấn không gian cục bộ.

2. Cải tiến thuật toán tìm đường BFS:
   - Chỉnh sửa: Đóng gói logic di chuyển dựa trên mảng Waypoints sinh ra từ BFS, giảm tải cho CPU khi quái vật di chuyển liên tục.

---

## 2. Quá trình thực hiện

### a. Tuần 1: Xây dựng nền tảng và Core Gameplay
- Kiến trúc phần mềm: Phân chia dự án thành các thư mục rõ ràng gồm Core xử lý engine và vòng lặp chính, Entities gồm Tháp, Quái, Đạn, Systems chứa logic Quản lý không gian, Quản lý tài nguyên và UI cho giao diện người dùng.
- Core Loop và Môi trường: Cài đặt Grid mang phong cách rừng xanh, khởi tạo cửa sổ Pygame ở độ phân giải 1080p, đồng bộ hóa FPS ở mức 60.
- Thực thể cơ bản: Tạo và lập trình logic cho các class Tower, Enemy, Projectile.
- Tương tác người dùng: Triển khai cơ chế tương tác bằng chuột toàn diện, click để đặt tháp, kiểm tra tính hợp lệ của tọa độ lưới, hover chuột lên các phần tử UI hoặc Tower để hiển thị Tooltips.
- Hệ thống AI cơ bản: Thiết lập hệ thống di chuyển cho Enemy theo Waypoints tiến về Base.
- Hệ thống Combat: Cài đặt logic dò tìm mục tiêu cho Tower. Quét bán kính xung quanh, chọn quái vật gần nhất tiến tới đích, xoay nòng và bắn đạn.

### b. Tuần 2: Nâng cao, Tối ưu hóa và Hoàn thiện UI/UX
- Nâng cấp Đồ họa Pixel Art thực thụ: Chuyển đổi từ việc vẽ đồ họa bằng code sang tích hợp hệ thống `AssetManager` nạp trực tiếp các texture Pixel Art chất lượng cao từ thư mục `assets/textures`. Hệ thống tự động xử lý độ trong suốt (alpha masking) và tối ưu hóa bounding box linh hoạt.
- Đồ họa và UI/UX: Tái cấu trúc toàn bộ đồ họa sang phong cách Fantasy với caro xanh lá đặc trưng. Hoàn thiện các thành phần UI với nút bấm phong cách đá/gỗ cứng cáp, tăng kích thước phông chữ dễ đọc, hệ thống Tooltip cập nhật thời gian thực các chỉ số DPS, Damage, Range.
- Tối ưu hóa sâu: Tích hợp thành công kiến trúc SpatialManager xử lý va chạm và tìm kiếm mục tiêu. Xóa bỏ các vấn đề rớt FPS ở cuối game.
- Chiều sâu chiến thuật: Lập trình Scrollable Inventory. Ra mắt Beacon và Hệ thống trang bị Gem cho phép gắn ngọc vào tháp trực tiếp bằng cách kéo thả.
- Hiệu ứng Nghe và Nhìn: Triển khai programmatic VFXManager tạo ra vô số các mảnh vỡ nhỏ khi đạn nổ, và Floating Text bay lên cho từng điểm sát thương. Thêm các hiệu ứng âm thanh SFX cho từng thao tác.
- Tự động hóa: Hoàn thiện và tinh chỉnh chế độ Auto giúp game tự động chơi, làm phong phú cách thưởng thức của người dùng.
- Cân bằng Game: Tinh chỉnh các tham số máu, sát thương qua từng Wave để tạo thử thách tăng dần nhưng không gây ức chế.

---

## 3. Kết quả đạt được
- Hoàn thành một engine Tower Defense bằng Pygame ở độ phân giải 1080p cực kỳ tối ưu và ổn định, duy trì tốc độ khung hình tuyệt đối kể cả trong các kịch bản hỗn loạn với số lượng lớn thực thể.
- Gameplay sở hữu chiều sâu chiến thuật vượt trội so với các tựa game cơ bản nhờ sự kết hợp giữa Adjacency Buff và Hệ thống Gem.
- Giao diện vô cùng thân thiện, nhất quán với phong cách đồ họa Fantasy tươi sáng. Mọi tương tác của người chơi đều nhận được phản hồi trực quan từ Tooltips và VFX thời gian thực.
- Mã nguồn được kiến trúc theo tiêu chuẩn Lập trình hướng đối tượng OOP, sạch sẽ, dễ đọc, hạn chế tối đa circular dependency, dễ dàng mở rộng thêm các chủng loại tháp hay kẻ địch mới trong tương lai.
- Chế độ Auto hoạt động mượt mà, phân bổ vị trí cực kỳ trực quan và hợp lý.

---

## 4. Tài liệu tham khảo
1. Pygame Official Documentation: Tài liệu gốc tham khảo các hàm vẽ đồ họa Surface, Sprite, xử lý sự kiện Event, và Mixer âm thanh.
2. Game Programming Patterns của Robert Nystrom: Nền tảng tư duy để áp dụng các Design Patterns vào game như Component, State, Object Pool dành cho đạn, Spatial Partition cho tối ưu va chạm.
3. Các tài liệu từ trang Red Blob Games về lý thuyết lưới và A Star Pathfinding.
4. Tài nguyên Pixel Art mang phong cách Fantasy tổng hợp từ cộng đồng làm game mở OpenGameArt và Itch.io.

---

## 5. Phụ lục 1: Kịch bản Demo
Phần này mô tả kịch bản trình bày các tính năng thực tế trong lúc báo cáo demo đồ án.

- Bắt đầu game: Màn hình chính hiện ra với Inventory trực quan bên góc màn hình và một bản đồ với lưới Forest Grid.
- Thao tác xem thông tin: Hover chuột lên các icon tháp trong kho đồ, một Tooltip tinh xảo sẽ hiện ra kèm mô tả kỹ năng, lượng sát thương, tốc độ bắn và tầm hoạt động.
- Thao tác xây tháp chiến thuật: Click chọn một Archer Tower và rê chuột vào bản đồ. Tầm hoạt động Range hiện lên một vòng tròn mờ. Người chơi click xuống để xây dựng tháp ở các khúc cua chữ U để tối ưu hóa thời gian bắn.
- Thao tác trang bị vật phẩm: Quái vật bắt đầu Spawn. Người chơi xây thêm một Beacon bên cạnh tháp bắn cung. Ngay lập tức, tháp bắn cung xuất hiện hiệu ứng buff, tốc độ bắn trong Tooltip tăng lên kèm chỉ số màu xanh lá. Tiếp tục thao tác click vào biểu tượng Fire Gem và gắn vào tháp để đòn bắn đổi màu và gây thêm sát thương đốt cháy.
- Kiểm chứng VFX và Hiệu năng: Quái vật chết nổ tung thành các mảnh nhỏ Particle System kèm các con số sát thương bay lên không trung rồi mờ dần. Mọi thứ diễn ra ở mức 60 FPS mượt mà.
- Chế độ Auto: Click vào nút AUTO ENABLED. Lập tức hệ thống tự quét bản đồ, tự động mua thêm tháp phòng thủ điền vào các vị trí trống xung quanh Beacon. Đây là màn phô diễn giải thuật Deterministic slotting rất trơn tru.

---

## 6. Phụ lục 2: Danh sách Docstrings Toàn diện của Hệ thống

Dưới đây là tập hợp đầy đủ docstrings của các thành phần cốt lõi trong engine game theo chuẩn Google Docstring.

### a. Hệ thống Tối ưu Không gian (SpatialManager)
```python
class SpatialManager:
    """
    Quản lý việc phân vùng không gian để tối ưu hóa kiểm tra va chạm Spatial Hashing.
    Thay vì duyệt số mũ bậc 2 giữa đạn và quái vật, SpatialManager chia màn hình thành một 
    lưới các cells lớn. Mỗi entity sẽ tự động được đăng ký vào cell tương ứng.
    
    Attributes:
        cell_size (int): Kích thước pixel của mỗi cell.
        grid (dict): Hash map lưu trữ danh sách entities theo cell.
    """
    def get_nearby_entities(self, x: float, y: float, radius: float) -> list:
        """
        Truy xuất nhanh danh sách các entities nằm trong vùng lân cận.
        
        Args:
            x (float): Tọa độ X trung tâm.
            y (float): Tọa độ Y trung tâm.
            radius (float): Bán kính quét.
            
        Returns:
            list: Danh sách các entities trong tầm quét.
        """
        pass

    def get_closest_entity(self, x: float, y: float, radius: float, criteria=None) -> object:
        """
        Tìm thực thể gần nhất trong bán kính cho trước.
        """
        pass
```

### b. Hệ thống Tìm đường (Pathfinding)
```python
def get_path_bfs(start_grid: tuple, end_grid: tuple, walkable_grid: set) -> list:
    """
    Thuật toán tìm đường Breadth-First Search (BFS) trên lưới không trọng số.
    
    Args:
        start_grid (tuple): Tọa độ ô bắt đầu (col, row).
        end_grid (tuple): Tọa độ ô đích (col, row).
        walkable_grid (set): Tập hợp ô có thể di chuyển.
        
    Returns:
        list: Danh sách các ô tạo thành đường đi ngắn nhất.
    """
    pass
```

### c. Thực thể Tháp phòng thủ (Tower)
```python
class Tower:
    """
    Đại diện cho công trình phòng thủ. Tự động bắn kẻ địch và nhận các nâng cấp.
    """
    def recalculate(self, adjacency_buffs: list) -> None:
        """
        Tính toán lại toàn bộ chỉ số sau khi nhận Buff từ Beacon hoặc Gem.
        """
        pass

    def find_target(self, spatial_manager: SpatialManager) -> object:
        """
        Tìm kiếm mục tiêu tối ưu dựa trên Targeting Mode đã thiết lập.
        """
        pass
```

### d. Thực thể Kẻ địch (Enemy)
```python
class Enemy:
    """
    Đại diện cho quái vật tấn công căn cứ.
    """
    def take_damage(self, amount: float, fire_mod: bool = False, ice_mod: bool = False) -> None:
        """
        Trừ máu kẻ địch và kích hoạt các hiệu ứng trạng thái (đốt, làm chậm).
        """
        pass
```

### e. Quản lý Tài nguyên (AssetManager)
```python
class AssetManager:
    """
    Singleton quản lý nạp và lưu trữ Assets (hình ảnh, âm thanh) từ thư mục `assets/`.
    """
    def _extract_sprites(self, path: str, expected_count: int) -> list:
        """
        Cắt sprite sheet và khử màu nền trắng không mong muốn.
        """
        pass
```

### f. Quản lý Hiệu ứng (VFXManager)
```python
class VFXManager:
    """
    Xử lý hạt nổ Particle và chữ nổi FloatingText sử dụng Object Pooling.
    """
    def create_explosion(self, x: float, y: float, color: tuple, count: int = 15) -> None:
        """
        Tạo hiệu ứng nổ tung tóe các hạt.
        """
        pass
```
### g. Quản lý Đợt quái (WaveManager)
```python
class WaveManager:
    """
    Quản lý luồng spawn quái vật, cấp phát phần thưởng và theo dõi trạng thái wave.
    """
    def spawn_enemy(self, waypoint_list: list) -> None:
        """
        Sinh ra kẻ địch tại điểm bắt đầu dựa trên chỉ số nâng cấp theo wave.
        """
        pass
```

### h. Công trình hỗ trợ (Beacon)
```python
class Beacon:
    """
    Tạo hiệu ứng hào quang (aura) tăng cường chỉ số cho các tháp phòng thủ lân cận.
    """
    def get_all_buffs(self) -> dict:
        """
        Tổng hợp tất cả buff hiện có từ beacon cơ bản và các thẻ nâng cấp đính kèm.
        """
        pass
```

### i. Đạn bắn (Projectile)
```python
class Projectile:
    """
    Thực thể đạn di chuyển bám đuổi theo kẻ địch.
    """
    def hit(self, spatial_manager: SpatialManager, vfx_manager: VFXManager) -> None:
        """
        Xử lý va chạm, trừ máu kẻ địch và kích nổ hiệu ứng diện rộng.
        """
        pass
```

### j. Quản lý Inventory (InventoryItem)
```python
class InventoryItem:
    """
    Mô tả thuộc tính và tác dụng của các trang bị trong hòm đồ.
    """
    def get_tooltip_data(self, t: callable) -> list:
        """
        Trích xuất văn bản hiển thị thông tin chi tiết của vật phẩm.
        """
        pass
```
