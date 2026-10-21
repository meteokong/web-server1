import { useId, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export interface RegisterFormValues {
  email: string;
  password: string;
}

export interface RegisterFormProps {
  /** Called with the entered credentials on submit. Reject to show an error. */
  onSubmit: (values: RegisterFormValues) => Promise<void>;
}

/**
 * Presentational/interactive register form. Knows nothing about the auth
 * API — it just collects email/password and delegates to onSubmit, which
 * the page (T035) wires to auth-service's register().
 */
export function RegisterForm({ onSubmit }: RegisterFormProps) {
  const emailId = useId();
  const passwordId = useId();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await onSubmit({ email, password });
    } catch (err) {
      setError(err instanceof Error ? err.message : "회원가입에 실패했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div>
        <label htmlFor={emailId}>이메일</label>
        <Input
          id={emailId}
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor={passwordId}>비밀번호</label>
        <Input
          id={passwordId}
          type="password"
          autoComplete="new-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      {error && <p role="alert">{error}</p>}
      <Button type="submit" disabled={isSubmitting}>
        가입하기
      </Button>
    </form>
  );
}
