import { FormEvent, useState } from "react";
import useSWR from "swr";

import { Layout } from "../components/Layout";
import { GrantMatchList } from "../components/GrantMatchList";
import { getMatches, GrantMatch } from "../lib/api";

export default function MatchesPage() {
  const [userId, setUserId] = useState<string>("");
  const [topK, setTopK] = useState<number>(5);
  const [shouldFetch, setShouldFetch] = useState(false);

  const { data, error, mutate, isLoading } = useSWR<GrantMatch[] | null>(
    shouldFetch ? ["/matches", userId, topK] : null,
    () => getMatches(Number(userId), topK)
  );

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setShouldFetch(true);
    mutate();
  }

  return (
    <Layout>
      <section>
        <h2>Get Personalized Matches</h2>
        <form className="card" onSubmit={handleSubmit}>
          <label>
            User ID
            <input
              required
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
            />
          </label>
          <label>
            Number of matches
            <input
              type="number"
              min={1}
              max={20}
              value={topK}
              onChange={(event) => setTopK(Number(event.target.value))}
            />
          </label>
          <button className="button" type="submit">
            Fetch matches
          </button>
        </form>
        {error && <p>Failed to load matches: {error.message}</p>}
        {isLoading && <p>Loading...</p>}
        {data && <GrantMatchList matches={data} />}
      </section>
    </Layout>
  );
}
