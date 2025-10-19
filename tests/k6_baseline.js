import http from 'k6/http';
import { check, sleep } from 'k6';

// ======== Test Options ========
export const options = {
  scenarios: {
    baseline: {
      executor: 'ramping-vus',
      stages: [
        { duration: '1m', target: 50 }, // ramp up
        { duration: '3m', target: 50 }, // sustain load
        { duration: '1m', target: 0 },  // ramp down
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.02'],     // <2% errors allowed
    http_req_duration: ['p(95)<800'],   // 95% under 800ms
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

  // Visit homepage (sets session)
  let res = http.get(`${BASE}/`, { jar });
  check(res, { 'home OK': (r) => r.status === 200 });

  // Randomly browse 1–3 products
  for (let i = 0; i < Math.floor(Math.random() * 3) + 1; i++) {
    const product = products[Math.floor(Math.random() * products.length)];
    res = http.get(`${BASE}/product/${product}`, { jar });
    check(res, { 'product OK': (r) => r.status === 200 });
    sleep(0.5);
  }

  // Add to cart (multipart/form-data)
  const addToCartForm = { product_id: pid, quantity: 1 };
  res = http.post(`${BASE}/cart`, addToCartForm, { jar });
  check(res, { 'add to cart OK': (r) => r.status === 200 || r.status === 302 });

  // View cart
  res = http.get(`${BASE}/cart`, { jar });
  check(res, { 'view cart OK': (r) => r.status === 200 });

  // Checkout (multipart/form-data)
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

  // Pause 1–3 seconds before next iteration
  sleep(Math.random() * 2 + 1);
}
