import unittest

from csuite.onboarding.state_machine import OnboardingStateMachine, InvalidTransitionError


class TestClientOnboardingTransitions(unittest.TestCase):
    def test_must_start_at_payment_received(self):
        sm = OnboardingStateMachine("t1")
        with self.assertRaises(InvalidTransitionError):
            sm.transition("LIVE")

    def test_forward_only_no_skipping(self):
        sm = OnboardingStateMachine("t1")
        sm.transition("PAYMENT_RECEIVED")
        with self.assertRaises(InvalidTransitionError):
            sm.transition("SUBACCOUNT_CREATED")  # skips several required stages

    def test_full_happy_path_reaches_optimization(self):
        sm = OnboardingStateMachine("t1")
        for state in sm.primary_path:
            sm.transition(state)
        self.assertEqual(sm.current_state, "OPTIMIZATION")
        self.assertTrue(sm.is_live())

    def test_blocked_only_reachable_from_allowed_states(self):
        sm = OnboardingStateMachine("t1")
        sm.transition("PAYMENT_RECEIVED")
        with self.assertRaises(InvalidTransitionError):
            sm.transition("BLOCKED")  # not yet in an allowed state for BLOCKED

    def test_blocked_then_resume_returns_to_prior_state(self):
        sm = OnboardingStateMachine("t1")
        sm.transition("PAYMENT_RECEIVED")
        sm.transition("AGREEMENT_CONFIRMED")
        sm.transition("INTAKE_SENT")
        sm.transition("BLOCKED")
        self.assertEqual(sm.current_state, "BLOCKED")
        sm.resume()
        self.assertEqual(sm.current_state, "INTAKE_SENT")

    def test_canceled_is_terminal(self):
        sm = OnboardingStateMachine("t1")
        sm.transition("PAYMENT_RECEIVED")
        sm.transition("CANCELED")
        self.assertTrue(sm.is_terminal())


if __name__ == "__main__":
    unittest.main()
