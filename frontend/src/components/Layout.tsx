import Link from "next/link";
import { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

export function Layout({ children }: Props) {
  return (
    <>
      <header>
        <h1>Menmo Grants</h1>
        <nav>
          <Link href="/">Home</Link>
          <Link href="/onboarding">Onboarding</Link>
          <Link href="/grants">Grants</Link>
          <Link href="/matches">Matches</Link>
        </nav>
      </header>
      <main>{children}</main>
    </>
  );
}
