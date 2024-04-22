<script>
	import { goto } from '$app/navigation';
	import TypoLogo from '$components/primitive/TypoLogo.svelte';
	import { Heading, GradientButton } from 'flowbite-svelte';
	import { ArrowRightOutline } from 'flowbite-svelte-icons';
</script>

<div class="w-full min-h-screen flex flex-col justify-center items-center relative">
	<div class="text-center max-w-[100ch]">
		<TypoLogo size="large" class="mb-8"/>
		<GradientButton on:click={() => goto('/login')}>
			Go to Demo <ArrowRightOutline class="w-3.5 h-3.5 ms-2" />
		</GradientButton>
	</div>
</div>
