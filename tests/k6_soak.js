import http from 'k6/http';
import { check, sleep } from 'k6';

// ======== Test Configuration ========
export const options = {
  scenarios: {
    soak: {
      executor: 'ramping-vus',
      stages: [
        { duration: '5m', target: 50 },   // warm up
        { duration: '4h', target: 300 },   // steady-state load
        { duration: '5m', target: 0 },    // ramp down
      ],
      gracefulRampDown: '1m',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],      // expect <1% failure rate
    http_req_duration: ['p(95)<1000'],   // p95 latency <1s over long run
  },
};

// ======== Test Logic ========
const BASE = __ENV.BASE_URL;
const products = [
  'L9ECAV7KIM', '0PUK6V6EV0', '1YMWWN1N4O', '2ZYFJ3GM2N',
  '66VCHSJNUP', '6E92ZMYYFZ', '9SIQT8TOJO', 'LS4PSXUNUM',
];

export default function () {
  const jar = http.cookieJar();
  const pid = products[Math.floor(Math.random() * products.length)];

  // 1️⃣ Homepage (set cookie)
  let res = http.get(`${BASE}/`, { jar });
  check(res, { 'home OK': (r) => r.status === 200 });

  // 2️⃣ View a random product
  const product = products[Math.floor(Math.random() * products.length)];
  res = http.get(`${BASE}/product/${product}`, { jar });
  check(res, { 'product OK': (r) => r.status === 200 });

  // 3️⃣ Add to cart (multipart form)
  const addToCartForm = { product_id: pid, quantity: 1 };
  res = http.post(`${BASE}/cart`, addToCartForm, { jar });
  check(res, { 'add to cart OK': (r) => r.status === 200 || r.status === 302 });

  // 4️⃣ View cart
  res = http.get(`${BASE}/cart`, { jar });
  check(res, { 'view cart OK': (r) => r.status === 200 });

  // 5️⃣ Checkout (multipart form)
  const checkoutForm = {
    email: 'someone@example.com',
    street_address: '1600 Amphitheatre Parkway',
    zip_code: '94043',
    city: 'Mountain View',
    state: 'CA',
    country: 'United States',
    credit_card_number: '4432801561520454',
    credit_card_expiration_month: '10',
    credit_card_expiration_year: '2026',
    credit_card_cvv: '672',
  };
  res = http.post(`${BASE}/cart/checkout`, checkoutForm, { jar });
  check(res, { 'checkout OK': (r) => r.status === 200 || r.status === 302 });

  // Simulate user idle time (1–5 seconds)
  sleep(Math.random() * 4 + 1);
}
