import { FormEvent, useState } from "react";

import { Layout } from "../components/Layout";
import { createUser, UserPayload } from "../lib/api";

export default function OnboardingPage() {
  const [form, setForm] = useState<UserPayload>({
    name: "",
    email: "",
    interests: "",
    organization: "",
    goals: "",
  });
  const [status, setStatus] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("Submitting...");
    try {
      const user = await createUser(form);
      setStatus(`Profile saved! User ID: ${user.id}`);
    } catch (error) {
      setStatus((error as Error).message);
    }
  }

  return (
    <Layout>
      <section>
        <h2>Tell us about your organization</h2>
        <form className="card" onSubmit={handleSubmit}>
          <label>
            Name
            <input
              required
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
            />
          </label>
          <label>
            Email
            <input
              required
              type="email"
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
            />
          </label>
          <label>
            Organization
            <input
              value={form.organization}
              onChange={(event) => setForm({ ...form, organization: event.target.value })}
            />
          </label>
          <label>
            Interests
            <textarea
              required
              rows={3}
              value={form.interests}
              onChange={(event) => setForm({ ...form, interests: event.target.value })}
            />
          </label>
          <label>
            Goals
            <textarea
              rows={3}
              value={form.goals}
              onChange={(event) => setForm({ ...form, goals: event.target.value })}
            />
          </label>
          <button className="button" type="submit">
            Save profile
          </button>
        </form>
        {status && <p>{status}</p>}
      </section>
    </Layout>
  );
}
