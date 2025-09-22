import { GrantMatch } from "../lib/api";

interface Props {
  matches: GrantMatch[];
}

export function GrantMatchList({ matches }: Props) {
  if (matches.length === 0) {
    return <p>No matches yet. Submit your profile to get started!</p>;
  }

  return (
    <section>
      <h2>Recommended Matches</h2>
      {matches.map((match) => (
        <article className="card" key={match.grant.id}>
          <header style={{ marginBottom: "0.5rem" }}>
            <h3>{match.grant.title}</h3>
            <small>Score: {(match.score * 100).toFixed(0)}%</small>
          </header>
          <p>{match.grant.description}</p>
          {match.grant.focus_area && <p><strong>Focus:</strong> {match.grant.focus_area}</p>}
          {match.grant.sponsor && <p><strong>Sponsor:</strong> {match.grant.sponsor}</p>}
        </article>
      ))}
    </section>
  );
}
