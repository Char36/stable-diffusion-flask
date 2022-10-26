function imagine(e) {
    e.preventDefault();

    const prompt = $('#prompt').val();
    const height = $('#height').val();
    const width = $('#width').val();
    const samples = $('#samples').val();
    const rows = $('#rows').val();
    const iterations = $('#iterations').val();
    const guidanceScale = $('#guidance-scale').val();
    const samplingSteps = $('#sampling-steps').val();

    setIsLoading(true);

    const seedValue = $('#seed').val().trim();
    const seed = seedValue
        ? seedValue
        : null;

    const requestData = {
        prompt: prompt,
        H: parseInt(height),
        W: parseInt(width),
        n_samples: parseInt(samples),
        n_rows: parseInt(rows),
        n_iter: parseInt(iterations),
        seed: parseInt(seed),
        scale: parseInt(guidanceScale),
        ddim_steps: parseInt(samplingSteps)
    };

    $.ajax({
        url: '/imagine',
        type: 'POST',
        accept: 'application/json',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(requestData),
        dataType: 'json',
        success: (data) => {
            setIsLoading(false);

            if (data.error) {
                alert(data.error);
                return;
            }

            const imageContent = generateImageContent(data);
            $('#output').html(imageContent);
        },
        error: (request, error) => {
            setIsLoading(false);
            alert('something went wrong, check backend console');
        }
    });

    return false;
}

function setIsLoading(isLoading) {
    $('#imagine_button').attr("disabled", isLoading);
    $('#generating').prop('hidden', !isLoading);
    $('#imagine-spinner').prop('hidden', !isLoading)

    $('#prompt').attr('disabled', isLoading);
    $('#height').attr('disabled', isLoading);
    $('#width').attr('disabled', isLoading);
    $('#samples').attr('disabled', isLoading);
    $('#rows').attr('disabled', isLoading);
    $('#iterations').attr('disabled', isLoading);
    $('#seed').attr('disabled', isLoading);
    $('#guidance-scale').attr('disabled', isLoading);
    $('#sampling-steps').attr('disabled', isLoading);

    if (isLoading) {
        $('#imagine-text').val("Loading...");
    } else {
        $('#imagine-text').val("Imagine");
    }
}

function generateImageContent(data) {
    return `
        <div>
            ${data.map(generateSingleImageContent).join('')}
        </div>
    `
}

function generateSingleImageContent(b64, i) {
    // Generate a unique filename w/ timestamp and sample index
    const fileName = `${Date.now()}-${i}.png`;
    const href = `data:image/png;base64,${b64}`;

    return ` 
        <a href="${href}" download="${fileName}" class="output-img">
            <img src="${href}" alt="img"/>
        </a>
    `
}
