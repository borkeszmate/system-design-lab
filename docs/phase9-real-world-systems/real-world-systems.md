# Phase 9: Real-World System Design

## Overview

Applying distributed systems concepts to real-world applications. This phase analyzes the architecture of large-scale systems and the engineering trade-offs involved.

**Key Learning:** Understanding how tech companies solve specific scalability and reliability challenges.

---

## Table of Contents

1. [URL Shortener (like bit.ly)](#1-url-shortener-like-bitly)
2. [Social Media Feed (like Twitter)](#2-social-media-feed-like-twitter)
3. [Video Streaming (like YouTube)](#3-video-streaming-like-youtube)
4. [E-commerce Platform (like Amazon)](#4-e-commerce-platform-like-amazon)
5. [Ride-Sharing (like Uber)](#5-ride-sharing-like-uber)
6. [Messaging System (like WhatsApp)](#6-messaging-system-like-whatsapp)

---

## 1. URL Shortener (like bit.ly)

### 1.1 Requirements

**Functional:**
- Create short URLs from long URLs
- Redirect short URLs to original URLs
- Custom short URLs (optional)
- Analytics (click tracking)

**Non-Functional:**
- **Scale:** 100M URLs created/month, 10B redirects/month
- **Latency:** < 10ms for redirects
- **Availability:** 99.99%

### 1.2 Capacity Estimation

```
Write (URL creation):
- 100M URLs/month = ~40 URLs/second
- Storage per URL: ~500 bytes (URL + metadata)
- Storage needed: 100M * 500B * 12 months * 10 years = ~600GB

Read (Redirects):
- 10B redirects/month = ~4000 redirects/second
- Peak: ~12,000 redirects/second
- Read:Write ratio = 100:1
```

### 1.3 API Design

```python
# Create short URL
POST /api/shorten
Request:
{
    "url": "https://example.com/very-long-url",
    "custom_alias": "mylink",  # optional
    "expiration": "2024-12-31"  # optional
}

Response:
{
    "short_url": "https://short.ly/abc123",
    "created_at": "2024-01-15T10:30:00Z"
}

# Redirect
GET /{short_code}
Response: 302 Redirect to original URL

# Analytics
GET /api/analytics/{short_code}
Response:
{
    "clicks": 1523,
    "unique_visitors": 892,
    "referrers": {
        "twitter.com": 450,
        "facebook.com": 312
    },
    "geo": {
        "US": 600,
        "UK": 200
    }
}
```

### 1.4 Short Code Generation

**Base62 Encoding:**

```python
import hashlib

class ShortCodeGenerator:
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    BASE = len(ALPHABET)

    def encode(self, num: int) -> str:
        """Convert number to base62 string"""
        if num == 0:
            return self.ALPHABET[0]

        result = []
        while num > 0:
            remainder = num % self.BASE
            result.append(self.ALPHABET[remainder])
            num //= self.BASE

        return ''.join(reversed(result))

    def decode(self, code: str) -> int:
        """Convert base62 string to number"""
        num = 0
        for char in code:
            num = num * self.BASE + self.ALPHABET.index(char)
        return num

    def generate_from_id(self, url_id: int) -> str:
        """Generate 7-character code from auto-increment ID"""
        # 62^7 = 3.5 trillion combinations
        return self.encode(url_id).rjust(7, '0')

    def generate_from_hash(self, url: str) -> str:
        """Generate from MD5 hash (collision possible)"""
        hash_digest = hashlib.md5(url.encode()).hexdigest()
        # Take first 7 characters
        num = int(hash_digest[:7], 16)
        return self.encode(num)[:7]


# Usage
generator = ShortCodeGenerator()

# Method 1: Auto-increment ID (no collisions)
url_id = 12345678
short_code = generator.generate_from_id(url_id)  # "aBc123"

# Method 2: Hash-based (handle collisions)
url = "https://example.com/page"
short_code = generator.generate_from_hash(url)
```

### 1.5 Database Schema

```sql
-- URLs table
CREATE TABLE urls (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    click_count BIGINT DEFAULT 0,
    INDEX idx_short_code (short_code),
    INDEX idx_user_id (user_id)
);

-- Analytics table (for detailed tracking)
CREATE TABLE clicks (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) NOT NULL,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    referrer TEXT,
    country VARCHAR(2),
    INDEX idx_short_code (short_code),
    INDEX idx_clicked_at (clicked_at)
) PARTITION BY RANGE (clicked_at);
```

### 1.6 System Architecture

```
┌──────────┐
│  Client  │
└────┬─────┘
     │
     ├─ POST /shorten ────▶ ┌──────────────┐      ┌──────────┐
     │                       │ API Gateway  │──────│ Write DB │
     │                       │   (Rate      │      │(PostgreSQL)
     │                       │   Limiting)  │      └──────────┘
     │                       └──────────────┘
     │
     └─ GET /{code} ───────▶ ┌──────────────┐      ┌──────────┐
                              │ CDN/Cache    │◀─────│ Read DB  │
                              │  (Redis)     │      │(Replicas)│
                              └──────────────┘      └──────────┘
                                     │
                                     ▼
                              302 Redirect
```

### 1.7 Caching Strategy

```python
import redis

class URLShortener:
    def __init__(self):
        self.redis = redis.Redis()
        self.db = get_db_connection()

    def get_original_url(self, short_code: str) -> str:
        # Try cache first
        cache_key = f"url:{short_code}"
        cached_url = self.redis.get(cache_key)

        if cached_url:
            # Increment counter asynchronously
            self.increment_click_count_async(short_code)
            return cached_url.decode('utf-8')

        # Cache miss - query database
        result = self.db.query(
            "SELECT original_url FROM urls WHERE short_code = %s",
            (short_code,)
        )

        if not result:
            raise NotFoundException(f"Short code {short_code} not found")

        original_url = result[0]['original_url']

        # Cache for 1 hour
        self.redis.setex(cache_key, 3600, original_url)

        # Increment counter
        self.increment_click_count_async(short_code)

        return original_url

    def increment_click_count_async(self, short_code: str):
        """Increment click count asynchronously"""
        # Use message queue to avoid blocking redirect
        message_queue.publish({
            'event': 'url_clicked',
            'short_code': short_code,
            'timestamp': time.time()
        })
```

---

## 2. Social Media Feed (like Twitter)

### 2.1 Requirements

**Functional:**
- Post tweets (140 characters)
- Follow/unfollow users
- View home timeline (tweets from followed users)
- View user timeline (user's own tweets)

**Non-Functional:**
- **Scale:** 500M users, 100M daily active
- **Latency:** < 500ms for timeline
- **Availability:** 99.95%

### 2.2 Fan-out Strategies

**Fan-out on Write (Push model):**

```python
def post_tweet(user_id: str, tweet_content: str):
    # 1. Save tweet to database
    tweet_id = save_tweet(user_id, tweet_content)

    # 2. Get user's followers
    follower_ids = get_followers(user_id)

    # 3. Fan-out: Add tweet to each follower's timeline
    for follower_id in follower_ids:
        add_to_timeline(follower_id, tweet_id)

    # Pros: Fast read (timeline already built)
    # Cons: Slow write (must update all followers' timelines)
    #       Expensive for celebrities (millions of followers)
```

**Fan-out on Read (Pull model):**

```python
def get_timeline(user_id: str, limit: int = 50):
    # 1. Get list of followed users
    following_ids = get_following(user_id)

    # 2. Get recent tweets from each followed user
    all_tweets = []
    for following_id in following_ids:
        tweets = get_user_tweets(following_id, limit=10)
        all_tweets.extend(tweets)

    # 3. Sort by timestamp and return top N
    all_tweets.sort(key=lambda t: t['created_at'], reverse=True)
    return all_tweets[:limit]

    # Pros: Fast write, scales with celebrities
    # Cons: Slow read (must query multiple users)
```

**Hybrid Approach (Twitter's actual approach):**

```python
def post_tweet(user_id: str, tweet_content: str):
    tweet_id = save_tweet(user_id, tweet_content)
    follower_count = get_follower_count(user_id)

    if follower_count < 10000:
        # Regular user: Fan-out on write
        follower_ids = get_followers(user_id)
        for follower_id in follower_ids:
            add_to_timeline(follower_id, tweet_id)
    else:
        # Celebrity: Fan-out on read
        # Just save tweet, don't push to followers
        pass

def get_timeline(user_id: str, limit: int = 50):
    # 1. Get pre-computed timeline (from fan-out on write)
    timeline = get_cached_timeline(user_id, limit)

    # 2. Merge with tweets from celebrities (fan-out on read)
    celebrity_following = get_celebrity_following(user_id)
    for celebrity_id in celebrity_following:
        recent_tweets = get_user_tweets(celebrity_id, limit=10)
        timeline.extend(recent_tweets)

    # 3. Sort and return
    timeline.sort(key=lambda t: t['created_at'], reverse=True)
    return timeline[:limit]
```

### 2.3 Database Schema

```sql
-- Users table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tweets table
CREATE TABLE tweets (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    content VARCHAR(280) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_created (user_id, created_at DESC)
) PARTITION BY RANGE (created_at);

-- Follows table (graph structure)
CREATE TABLE follows (
    follower_id BIGINT NOT NULL REFERENCES users(id),
    following_id BIGINT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id),
    INDEX idx_follower (follower_id),
    INDEX idx_following (following_id)
);

-- Timeline cache (Redis)
Key: timeline:{user_id}
Value: [tweet_id_1, tweet_id_2, ..., tweet_id_N]  # Sorted by timestamp
```

### 2.4 System Architecture

```
┌──────────┐
│  Client  │
└────┬─────┘
     │
     ├─ POST /tweet ───────▶ ┌─────────────┐      ┌───────────┐
     │                        │  API Server │──────│  Tweet DB │
     │                        └──────┬──────┘      └───────────┘
     │                               │
     │                               ▼
     │                        ┌─────────────┐
     │                        │ Fan-out     │
     │                        │ Worker      │
     │                        └──────┬──────┘
     │                               │
     │                               ▼
     │                        ┌─────────────┐
     │                        │ Timeline    │
     │                        │ Cache       │
     │                        │ (Redis)     │
     │                        └─────────────┘
     │
     └─ GET /timeline ───────▶ ┌─────────────┐
                                │ Timeline    │
                                │ Service     │
                                └─────────────┘
```

---

## 3. Video Streaming (like YouTube)

### 3.1 Requirements

**Functional:**
- Upload videos
- Stream videos
- Search videos
- Recommendations

**Non-Functional:**
- **Scale:** 500 hours of video uploaded per minute
- **Latency:** < 2s to start playback
- **Storage:** Petabyte scale

### 3.2 Video Processing Pipeline

```python
def process_uploaded_video(video_id: str, original_file_path: str):
    """
    Multi-step video processing pipeline
    """
    # 1. Validate and analyze video
    metadata = analyze_video(original_file_path)

    # 2. Generate thumbnails (at different timestamps)
    thumbnails = generate_thumbnails(original_file_path, times=[1, 5, 10])

    # 3. Transcode to multiple resolutions (ABR)
    resolutions = [
        ('1080p', 1920, 1080, '5000k'),
        ('720p', 1280, 720, '2500k'),
        ('480p', 854, 480, '1000k'),
        ('360p', 640, 360, '500k')
    ]

    for name, width, height, bitrate in resolutions:
        output_path = f"/processed/{video_id}/{name}.mp4"
        transcode_video(
            original_file_path,
            output_path,
            width=width,
            height=height,
            bitrate=bitrate
        )

    # 4. Generate HLS/DASH manifests for adaptive streaming
    generate_hls_manifest(video_id, resolutions)

    # 5. Upload to CDN
    upload_to_cdn(video_id)

    # 6. Update database
    mark_video_as_ready(video_id, metadata)
```

### 3.3 Adaptive Bitrate Streaming (HLS)

```
# master.m3u8 (playlist of playlists)
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
1080p/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
720p/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=854x480
480p/index.m3u8

# 1080p/index.m3u8 (segments list)
#EXTM3U
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
segment_0.ts
#EXTINF:10.0,
segment_1.ts
#EXTINF:10.0,
segment_2.ts
```

**Player behavior:**
- Start with lowest quality (360p) for fast startup
- Measure bandwidth
- Upgrade to 480p, 720p, 1080p as bandwidth allows
- Downgrade if buffering occurs

### 3.4 CDN Architecture

```
┌──────────┐
│  User    │
└────┬─────┘
     │
     ▼
┌─────────────┐  Cache Miss   ┌──────────────┐  Cache Miss   ┌──────────┐
│ Edge CDN    │ ───────────▶  │ Regional CDN │ ───────────▶  │  Origin  │
│ (Closest)   │               │              │               │  Server  │
└─────────────┘               └──────────────┘               └──────────┘
     │                               │                              │
     │ Cache Hit                     │ Cache Hit                    │
     ▼                               ▼                              │
┌─────────────┐               ┌──────────────┐                     │
│ Serve video │               │  Pull from   │                     │
│ from cache  │               │   edge CDN   │                     │
└─────────────┘               └──────────────┘                     │
                                                                    │
                              ┌──────────────────────────────────┐ │
                              │ Object Storage (S3, GCS)         │◀┘
                              │ - Replicated across regions      │
                              │ - Lifecycle policies (archive)   │
                              └──────────────────────────────────┘
```

### 3.5 Database Schema

```sql
-- Videos table
CREATE TABLE videos (
    id VARCHAR(20) PRIMARY KEY,  -- e.g., "dQw4w9WgXcQ"
    user_id BIGINT NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    duration_seconds INT NOT NULL,
    view_count BIGINT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'processing',  -- processing, ready, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at DESC)
);

-- Video files (different resolutions)
CREATE TABLE video_files (
    id BIGSERIAL PRIMARY KEY,
    video_id VARCHAR(20) NOT NULL REFERENCES videos(id),
    resolution VARCHAR(10) NOT NULL,  -- 1080p, 720p, etc.
    file_size_bytes BIGINT NOT NULL,
    cdn_url TEXT NOT NULL,
    INDEX idx_video_id (video_id)
);
```

---

## 4. E-commerce Platform (like Amazon)

### 4.1 Requirements

**Functional:**
- Product catalog
- Shopping cart
- Order processing
- Payment
- Inventory management

**Non-Functional:**
- **Scale:** 100M products, 10M daily orders
- **Consistency:** Strong for inventory and payments
- **Availability:** 99.99%

### 4.2 Inventory Management (Preventing Overselling)

```python
from typing import List

class InventoryService:
    def reserve_inventory(self, order_items: List[dict]) -> bool:
        """
        Atomically reserve inventory for order.
        Uses pessimistic locking to prevent overselling.
        """
        with db.transaction():
            for item in order_items:
                product_id = item['product_id']
                quantity = item['quantity']

                # Lock row for update
                result = db.query("""
                    SELECT quantity
                    FROM inventory
                    WHERE product_id = %s
                    FOR UPDATE  -- Pessimistic lock
                """, (product_id,))

                available_quantity = result[0]['quantity']

                if available_quantity < quantity:
                    # Not enough stock
                    db.rollback()
                    return False

                # Decrease inventory
                db.execute("""
                    UPDATE inventory
                    SET quantity = quantity - %s,
                        reserved = reserved + %s
                    WHERE product_id = %s
                """, (quantity, quantity, product_id))

            db.commit()
            return True

    def release_reservation(self, order_items: List[dict]):
        """Release reserved inventory (if payment fails)"""
        with db.transaction():
            for item in order_items:
                db.execute("""
                    UPDATE inventory
                    SET quantity = quantity + %s,
                        reserved = reserved - %s
                    WHERE product_id = %s
                """, (item['quantity'], item['quantity'], item['product_id']))
            db.commit()
```

### 4.3 Order Processing Saga

```python
from enum import Enum

class OrderStatus(Enum):
    CREATED = "created"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderSaga:
    """
    Orchestrate distributed transaction across services.
    If any step fails, execute compensating transactions.
    """

    def create_order(self, user_id: str, items: List[dict]) -> str:
        order_id = None

        try:
            # Step 1: Create order
            order_id = order_service.create_order(user_id, items)

            # Step 2: Reserve inventory
            if not inventory_service.reserve_inventory(items):
                raise InventoryError("Insufficient stock")

            # Step 3: Process payment
            payment_result = payment_service.charge(user_id, calculate_total(items))
            if not payment_result.success:
                raise PaymentError("Payment failed")

            # Step 4: Update order status
            order_service.update_status(order_id, OrderStatus.PAID)

            # Step 5: Trigger fulfillment
            fulfillment_service.create_shipment(order_id)

            return order_id

        except (InventoryError, PaymentError) as e:
            # Compensating transactions (rollback)
            if order_id:
                self.cancel_order(order_id, reason=str(e))
            raise

    def cancel_order(self, order_id: str, reason: str):
        """Compensating transaction"""
        # 1. Refund payment (if charged)
        payment_service.refund(order_id)

        # 2. Release inventory reservation
        items = order_service.get_order_items(order_id)
        inventory_service.release_reservation(items)

        # 3. Update order status
        order_service.update_status(order_id, OrderStatus.CANCELLED, reason)
```

### 4.4 Product Search (Elasticsearch)

```python
from elasticsearch import Elasticsearch

class ProductSearch:
    def __init__(self):
        self.es = Elasticsearch(['elasticsearch:9200'])

    def index_product(self, product: dict):
        """Index product for search"""
        self.es.index(
            index='products',
            id=product['id'],
            document={
                'name': product['name'],
                'description': product['description'],
                'category': product['category'],
                'price': product['price'],
                'rating': product['rating'],
                'in_stock': product['in_stock']
            }
        )

    def search(self, query: str, filters: dict = None, limit: int = 20):
        """Search products with filters"""
        body = {
            'query': {
                'bool': {
                    'must': [
                        {
                            'multi_match': {
                                'query': query,
                                'fields': ['name^3', 'description'],  # Boost name
                                'fuzziness': 'AUTO'  # Typo tolerance
                            }
                        }
                    ],
                    'filter': []
                }
            },
            'sort': [
                {'_score': {'order': 'desc'}},
                {'rating': {'order': 'desc'}}
            ],
            'size': limit
        }

        # Apply filters
        if filters:
            if 'category' in filters:
                body['query']['bool']['filter'].append({
                    'term': {'category': filters['category']}
                })

            if 'price_range' in filters:
                body['query']['bool']['filter'].append({
                    'range': {
                        'price': {
                            'gte': filters['price_range']['min'],
                            'lte': filters['price_range']['max']
                        }
                    }
                })

            if 'in_stock_only' in filters:
                body['query']['bool']['filter'].append({
                    'term': {'in_stock': True}
                })

        results = self.es.search(index='products', body=body)
        return [hit['_source'] for hit in results['hits']['hits']]
```

---

## 5. Ride-Sharing (like Uber)

### 5.1 Requirements

**Functional:**
- Request ride
- Match driver to rider
- Real-time location tracking
- Fare calculation
- Payment

**Non-Functional:**
- **Scale:** 10M daily rides
- **Latency:** < 3s for driver matching
- **Accuracy:** < 50m GPS accuracy

### 5.2 Geospatial Indexing (Finding Nearby Drivers)

**Geohashing:**

```python
import geohash2

class DriverLocationService:
    def __init__(self):
        self.redis = redis.Redis()

    def update_driver_location(self, driver_id: str, lat: float, lon: float):
        """Update driver location using geohash"""
        # Generate geohash (precision 6 = ~1.2km x 0.6km)
        geohash = geohash2.encode(lat, lon, precision=6)

        # Store in Redis sorted set by geohash
        self.redis.geoadd('drivers', lon, lat, driver_id)

        # Also store in hash for fast retrieval
        self.redis.hset(f"driver:{driver_id}", mapping={
            'lat': lat,
            'lon': lon,
            'geohash': geohash,
            'updated_at': time.time()
        })

    def find_nearby_drivers(
        self,
        lat: float,
        lon: float,
        radius_km: float = 5.0,
        limit: int = 10
    ) -> List[dict]:
        """Find drivers within radius"""
        # Use Redis GEORADIUS command
        nearby = self.redis.georadius(
            'drivers',
            lon, lat,
            radius_km, unit='km',
            withdist=True,
            sort='ASC',
            count=limit
        )

        drivers = []
        for driver_id, distance in nearby:
            driver_info = self.redis.hgetall(f"driver:{driver_id}")
            drivers.append({
                'driver_id': driver_id.decode('utf-8'),
                'distance_km': distance,
                'lat': float(driver_info[b'lat']),
                'lon': float(driver_info[b'lon'])
            })

        return drivers
```

### 5.3 Driver-Rider Matching

```python
class RideMatchingService:
    def match_driver(self, ride_request: dict) -> dict:
        """
        Match rider with best available driver.

        Factors:
        - Distance (primary)
        - Driver rating
        - Acceptance rate
        - Direction (if driver is already en route)
        """
        rider_lat = ride_request['pickup_lat']
        rider_lon = ride_request['pickup_lon']

        # Find nearby available drivers
        nearby_drivers = location_service.find_nearby_drivers(
            rider_lat, rider_lon,
            radius_km=5.0,
            limit=20
        )

        if not nearby_drivers:
            raise NoDriversAvailableError()

        # Score each driver
        scored_drivers = []
        for driver in nearby_drivers:
            # Check availability
            if not self.is_driver_available(driver['driver_id']):
                continue

            # Calculate score (lower is better)
            score = (
                driver['distance_km'] * 1.0 +        # Distance weight
                (5.0 - driver.get('rating', 5.0)) * 0.5 +  # Rating weight
                (1.0 - driver.get('acceptance_rate', 1.0)) * 0.3  # Acceptance weight
            )

            scored_drivers.append((driver, score))

        # Sort by score
        scored_drivers.sort(key=lambda x: x[1])

        # Try to assign to best driver
        for driver, score in scored_drivers[:5]:  # Try top 5
            if self.send_ride_request_to_driver(driver['driver_id'], ride_request):
                return driver

        raise NoDriversAcceptedError()
```

### 5.4 Real-Time Location Updates (WebSocket)

```python
from fastapi import WebSocket
import asyncio

class LocationTrackingService:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect_rider(self, ride_id: str, websocket: WebSocket):
        """Connect rider to receive real-time driver location updates"""
        await websocket.accept()
        self.active_connections[f"rider:{ride_id}"] = websocket

        try:
            while True:
                # Keep connection alive
                await asyncio.sleep(1)
        except Exception:
            del self.active_connections[f"rider:{ride_id}"]

    async def update_driver_location(
        self,
        ride_id: str,
        driver_id: str,
        lat: float,
        lon: float
    ):
        """Send driver location update to rider"""
        connection_key = f"rider:{ride_id}"

        if connection_key in self.active_connections:
            websocket = self.active_connections[connection_key]

            await websocket.send_json({
                'type': 'location_update',
                'driver_id': driver_id,
                'lat': lat,
                'lon': lon,
                'timestamp': time.time()
            })
```

---

## 6. Messaging System (like WhatsApp)

### 6.1 Requirements

**Functional:**
- One-to-one messaging
- Group messaging
- Message delivery confirmation
- Online/offline status
- Media sharing

**Non-Functional:**
- **Scale:** 2B users, 100B messages/day
- **Latency:** < 100ms message delivery
- **Delivery:** At-least-once guarantee

### 6.2 Message Delivery

```python
class MessageService:
    def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        message_type: str = 'text'
    ) -> str:
        """
        Send message with delivery guarantees
        """
        # 1. Generate message ID
        message_id = generate_uuid()

        # 2. Save to database
        message = {
            'id': message_id,
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'content': content,
            'type': message_type,
            'timestamp': time.time(),
            'status': 'sent'
        }
        db.insert('messages', message)

        # 3. Check if recipient is online
        if self.is_user_online(recipient_id):
            # Push immediately via WebSocket
            self.push_to_user(recipient_id, message)
        else:
            # Queue for later delivery
            message_queue.enqueue(recipient_id, message)

        # 4. Send push notification
        push_service.send_notification(recipient_id, {
            'title': f"New message from {sender_id}",
            'body': content[:50]
        })

        return message_id

    def acknowledge_delivery(self, message_id: str, user_id: str):
        """Mark message as delivered"""
        db.update('messages',
            {'id': message_id},
            {'status': 'delivered', 'delivered_at': time.time()}
        )

        # Notify sender
        message = db.get('messages', {'id': message_id})
        self.push_to_user(message['sender_id'], {
            'type': 'delivery_receipt',
            'message_id': message_id,
            'status': 'delivered'
        })

    def acknowledge_read(self, message_id: str, user_id: str):
        """Mark message as read"""
        db.update('messages',
            {'id': message_id},
            {'status': 'read', 'read_at': time.time()}
        )

        # Notify sender (blue checkmarks)
        message = db.get('messages', {'id': message_id})
        self.push_to_user(message['sender_id'], {
            'type': 'read_receipt',
            'message_id': message_id,
            'status': 'read'
        })
```

### 6.3 Message Storage (Cassandra)

```cql
-- Messages table (partitioned by user)
CREATE TABLE messages_by_user (
    user_id TEXT,
    timestamp TIMESTAMP,
    message_id UUID,
    sender_id TEXT,
    recipient_id TEXT,
    content TEXT,
    type TEXT,
    status TEXT,
    PRIMARY KEY (user_id, timestamp, message_id)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- Why Cassandra?
-- - Horizontal scalability (add nodes to scale)
-- - High write throughput (100B messages/day)
-- - Time-series data (messages ordered by timestamp)
-- - Partitioning by user_id (all user's messages on same node)
```

### 6.4 Online Presence

```python
class PresenceService:
    def __init__(self):
        self.redis = redis.Redis()

    def user_online(self, user_id: str):
        """Mark user as online"""
        # Set with expiration (heartbeat)
        self.redis.setex(f"online:{user_id}", 30, "1")

        # Notify contacts
        contacts = self.get_user_contacts(user_id)
        for contact_id in contacts:
            self.push_presence_update(contact_id, {
                'user_id': user_id,
                'status': 'online'
            })

    def heartbeat(self, user_id: str):
        """Refresh online status (called every 10 seconds)"""
        self.redis.expire(f"online:{user_id}", 30)

    def is_user_online(self, user_id: str) -> bool:
        """Check if user is online"""
        return self.redis.exists(f"online:{user_id}") == 1

    def get_online_contacts(self, user_id: str) -> List[str]:
        """Get list of user's contacts who are online"""
        contacts = self.get_user_contacts(user_id)
        return [c for c in contacts if self.is_user_online(c)]
```

---

## Summary and Key Takeaways

### Common Patterns

1. **Caching:** All systems use caching (Redis) for frequently accessed data
2. **CDN:** Video streaming and media-heavy apps rely on CDN
3. **Sharding:** Partition data by user_id or primary key
4. **Async Processing:** Use message queues for non-critical operations
5. **Eventual Consistency:** Accept for non-critical data (view counts, analytics)
6. **Strong Consistency:** Required for critical data (payments, inventory)

### Trade-offs

| System | Primary Challenge | Solution | Trade-off |
|--------|-------------------|----------|-----------|
| URL Shortener | Read-heavy | Aggressive caching | Stale click counts |
| Social Feed | Write amplification | Hybrid fan-out | Complex logic |
| Video Streaming | Storage cost | Lifecycle policies | Older videos slower |
| E-commerce | Inventory consistency | Pessimistic locks | Lower throughput |
| Ride-Sharing | Real-time matching | Geospatial indexing | Approximate distance |
| Messaging | Delivery guarantee | Message queue | Delayed delivery |

---

## Additional Resources

### Case Studies
- Netflix Tech Blog
- Uber Engineering Blog
- YouTube Architecture
- Amazon Architecture

### Books
- "System Design Interview" by Alex Xu
- "Designing Data-Intensive Applications"
