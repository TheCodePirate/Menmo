import Link from "next/link";

import { Layout } from "../components/Layout";

export default function HomePage() {
  return (
    <Layout>
      <section>
        <h2>Welcome to Menmo</h2>
        <p>
          Menmo pairs mission-driven organizations with funding opportunities using
          lightweight AI matching. Complete onboarding to share your focus areas,
          browse curated grants, and request personalized recommendations.
        </p>
        <Link className="button" href="/onboarding">
          Get Started
        </Link>
      </section>
    </Layout>
  );
}
