import useSWR from "swr";

import { Layout } from "../components/Layout";
import { Grant, listGrants } from "../lib/api";

export default function GrantsPage() {
  const { data, error } = useSWR<Grant[]>("/grants", () => listGrants());

  return (
    <Layout>
      <section>
        <h2>Browse Grants</h2>
        {error && <p>Failed to load grants: {error.message}</p>}
        {!data && !error && <p>Loading...</p>}
        {data &&
          data.map((grant) => (
            <article className="card" key={grant.id}>
              <h3>{grant.title}</h3>
              <p>{grant.description}</p>
              {grant.focus_area && <p><strong>Focus:</strong> {grant.focus_area}</p>}
              {grant.sponsor && <p><strong>Sponsor:</strong> {grant.sponsor}</p>}
            </article>
          ))}
      </section>
    </Layout>
  );
}
