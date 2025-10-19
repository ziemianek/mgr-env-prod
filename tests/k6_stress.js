import http from 'k6/http';
import { check, sleep } from 'k6';

// ======== Test Configuration ========
export const options = {
  scenarios: {
    stress_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 50 },   // warm-up
        { duration: '2m', target: 200 },  // moderate load
        { duration: '2m', target: 500 },  // high load
        { duration: '2m', target: 1000 },  // stress peak
        { duration: '2m', target: 2000 }, // maximum stress
        { duration: '1m', target: 0 },    // ramp down
      ],
      gracefulRampDown: '1m',
    },
  },
  thresholds: {
    http_req_failed: [
      'rate<0.10', // tolerate up to 10% errors at peak
    ],
    http_req_duration: [
      'p(95)<2000', // 95% of requests should finish under 2s
      'p(99)<4000', // 99% under 4s
    ]
  },
  discardResponseBodies: true,
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

  // 1️⃣ Visit homepage
  let res = http.get(`${BASE}/`, { jar });
  check(res, { 'home OK': (r) => r.status === 200 });

  // 2️⃣ Add product to cart (multipart form)
  const addToCartForm = { product_id: pid, quantity: 1 };
  res = http.post(`${BASE}/cart`, addToCartForm, { jar });
  check(res, { 'add to cart OK': (r) => r.status === 200 || r.status === 302 });

  // 3️⃣ View cart
  res = http.get(`${BASE}/cart`, { jar });
  check(res, { 'view cart OK': (r) => r.status === 200 });

  // 4️⃣ Checkout (multipart form)
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

  sleep(Math.random() * 2); // small think time
}
