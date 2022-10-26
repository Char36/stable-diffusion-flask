function imagine(e) {
    const prompt = $('#prompt');
    const height = $('#height');
    const width = $('#width');
    const samples = $('#samples');
    const rows = $('#rows');
    const iterations = $('#iterations');
    const imagine_button = $('#imagine_button');
    const generating = $('#generating');
    const output = $('#output')

    e.preventDefault();
    imagine_button.attr("disabled", true);

    const requestData = {
        prompt: prompt.val(),
        H: parseInt(height.val()),
        W: parseInt(width.val()),
        n_samples: parseInt(samples.val()),
        n_rows: parseInt(rows.val()),
        n_iter: parseInt(iterations.val())
    };

    generating.prop('hidden', false);

    $.ajax({
        url: '/imagine',
        type: 'POST',
        accept: 'application/json',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(requestData),
        dataType: 'json',
        success: (data) => {
            imagine_button.attr("disabled", false);
            generating.prop('hidden', true);

            const imageContent = generateImageContent(data);
            // (imageContent, '_blank', `width=${width},height=${height}`);
            output.html(imageContent);
        },
        error: (request, error) => {
            imagine_button.attr("disabled", false);
            generating.prop('hidden', true);
            alert('something went wrong, check backend console');
        }
    });

    return false;
}

function generateImageContent(data) {
    return `
        <div>
            ${data.map(b64 => `<img src="data:image/png;base64,${b64}" alt="img" class="output-img"/>`)}
        </div>
        `
}
